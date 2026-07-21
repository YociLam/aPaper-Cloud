#!/usr/bin/env python3
"""Fetch one CVF Open Access main-conference edition into import-json input."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
from html.parser import HTMLParser
import http.client
import json
from pathlib import Path
import re
import threading
import time
from typing import Iterable
from urllib.parse import urljoin, urlsplit


ORIGIN = "https://openaccess.thecvf.com"
USER_AGENT = "aPaper-Cloud-Metadata/1.0 (CVF Open Access sync)"
_thread_local = threading.local()


class IndexParser(HTMLParser):
    def __init__(self, conference: str, year: int) -> None:
        super().__init__()
        self._pattern = re.compile(
            rf"^/content/{re.escape(conference)}{year}/html/.+_{re.escape(conference)}_{year}_paper\.html$"
        )
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href") or ""
        if self._pattern.match(href):
            self.links.append(urljoin(ORIGIN, href))


class DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self._abstract_depth = 0
        self._abstract_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta":
            name = (values.get("name") or "").strip()
            content = (values.get("content") or "").strip()
            if name and content:
                self.meta.setdefault(name, []).append(content)
        if values.get("id") == "abstract":
            self._abstract_depth = 1
        elif self._abstract_depth:
            self._abstract_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._abstract_depth:
            self._abstract_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._abstract_depth:
            text = data.strip()
            if text:
                self._abstract_parts.append(text)

    @property
    def abstract(self) -> str:
        return " ".join(" ".join(self._abstract_parts).split())


def fetch_bytes(url: str, *, timeout: int, retries: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            parts = urlsplit(url)
            connection = getattr(_thread_local, "connection", None)
            if connection is None:
                connection = http.client.HTTPSConnection(parts.hostname, timeout=timeout)
                _thread_local.connection = connection
            path = parts.path + (f"?{parts.query}" if parts.query else "")
            connection.request(
                "GET",
                path,
                headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"},
            )
            response = connection.getresponse()
            body = response.read()
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
            if response.getheader("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
            return body
        except Exception as error:  # noqa: BLE001 - network errors vary by platform
            last_error = error
            connection = getattr(_thread_local, "connection", None)
            if connection is not None:
                connection.close()
                _thread_local.connection = None
            if attempt < retries:
                time.sleep(attempt)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def index_links(paths: Iterable[Path], conference: str, year: int) -> list[str]:
    links: set[str] = set()
    for path in paths:
        parser = IndexParser(conference, year)
        parser.feed(path.read_text(encoding="utf-8"))
        links.update(parser.links)
    return sorted(links)


def paper_id(url: str) -> str:
    filename = url.rsplit("/", 1)[-1]
    return filename.removesuffix(".html")


def fetch_paper(
    url: str,
    *,
    conference: str,
    year: int,
    cache_dir: Path,
    timeout: int,
    retries: int,
) -> dict[str, object]:
    cache_path = cache_dir / f"{paper_id(url)}.html"
    if cache_path.exists():
        html = cache_path.read_bytes()
    else:
        html = fetch_bytes(url, timeout=timeout, retries=retries)
        cache_path.write_bytes(html)

    parser = DetailParser()
    parser.feed(html.decode("utf-8", errors="replace"))
    title = (parser.meta.get("citation_title") or [""])[0].strip()
    authors = [value.strip() for value in parser.meta.get("citation_author", []) if value.strip()]
    pdf_url = (parser.meta.get("citation_pdf_url") or [""])[0].strip()
    published = (parser.meta.get("citation_publication_date") or [str(year)])[0].strip()
    if re.fullmatch(r"\d{4}", published):
        published = f"{published}-06-01T00:00:00Z"
    if not title or not authors or not parser.abstract or not pdf_url:
        raise RuntimeError(f"incomplete CVF metadata at {url}")
    return {
        "id": paper_id(url),
        "source_paper_id": paper_id(url),
        "doi": "",
        "title": title,
        "abstract": parser.abstract,
        "authors": authors,
        "categories": [],
        "published": published,
        "link": url,
        "pdf_url": pdf_url,
        "updated_at": published,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conference", default="CVPR", choices=["CVPR", "ICCV", "WACV", "ACCV"])
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--index-file", type=Path, action="append", required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retries", type=int, default=4)
    args = parser.parse_args()

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    links = index_links(args.index_file, args.conference, args.year)
    if not links:
        raise SystemExit("no CVF paper links found in the supplied index files")

    records: list[dict[str, object]] = []
    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(args.workers, 1)) as executor:
        futures = {
            executor.submit(
                fetch_paper,
                url,
                conference=args.conference,
                year=args.year,
                cache_dir=args.cache_dir,
                timeout=args.timeout,
                retries=max(args.retries, 1),
            ): url
            for url in links
        }
        for completed, future in enumerate(as_completed(futures), 1):
            url = futures[future]
            try:
                records.append(future.result())
            except Exception as error:  # noqa: BLE001 - report every failed source record
                failures.append((url, str(error)))
            if completed == 1 or completed % 100 == 0 or completed == len(futures):
                print(f"progress={completed}/{len(futures)} failures={len(failures)}", flush=True)

    if failures:
        for url, error in failures[:20]:
            print(f"failed url={url} error={error}", flush=True)
        raise SystemExit(f"CVF metadata fetch failed for {len(failures)} of {len(links)} papers")

    records.sort(key=lambda record: str(record["source_paper_id"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"record_count={len(records)}")


if __name__ == "__main__":
    main()
