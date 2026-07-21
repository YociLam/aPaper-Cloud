#!/usr/bin/env python3
"""Fetch one official Robotics: Science and Systems proceedings edition."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import threading
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ORIGIN = "https://roboticsproceedings.org"
USER_AGENT = "aPaper-Cloud-Metadata/1.0 (RSS proceedings sync)"
_thread_local = threading.local()


class IndexParser(HTMLParser):
    def __init__(self, series: str) -> None:
        super().__init__()
        self._pattern = re.compile(rf"^(?:\./)?{re.escape(series)}/p\d{{3}}\.html$|^p\d{{3}}\.html$")
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = (dict(attrs).get("href") or "").strip()
        if self._pattern.match(href):
            self.links.add(urljoin(f"{ORIGIN}/{self.series}/", href))

    @property
    def series(self) -> str:
        match = self._pattern.pattern.split("re.escape(series)", 1)
        del match
        return ""


class DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self._bold_depth = 0
        self._paragraph_depth = 0
        self._awaiting_abstract = False
        self._collect_abstract = False
        self._abstract_parts: list[str] = []
        self._pre_depth = 0
        self._pre_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta":
            name = (values.get("name") or "").strip()
            content = (values.get("content") or "").strip()
            if name and content:
                self.meta.setdefault(name, []).append(content)
        if tag == "b":
            self._bold_depth += 1
        if tag == "p":
            self._paragraph_depth += 1
            if self._awaiting_abstract:
                self._collect_abstract = True
                self._awaiting_abstract = False
        if tag == "pre":
            self._pre_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "b" and self._bold_depth:
            self._bold_depth -= 1
        if tag == "p" and self._paragraph_depth:
            if self._collect_abstract:
                self._collect_abstract = False
            self._paragraph_depth -= 1
        if tag == "pre" and self._pre_depth:
            self._pre_depth -= 1

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if self._bold_depth and text.casefold().rstrip(":") == "abstract":
            self._awaiting_abstract = True
        elif self._collect_abstract and text:
            self._abstract_parts.append(text)
        if self._pre_depth and text:
            self._pre_parts.append(text)

    @property
    def abstract(self) -> str:
        return " ".join(self._abstract_parts)

    @property
    def doi(self) -> str:
        match = re.search(r"10\.15607/RSS\.\d{4}\.[IVXLCDM]+\.\d{3}", " ".join(self._pre_parts), re.I)
        return match.group(0) if match else ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series", required=True, help="Official RSS series directory, e.g. rss21")
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--retries", type=int, default=3)
    return parser.parse_args()


def fetch(url: str, *, timeout: int, retries: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except Exception as error:  # noqa: BLE001 - URL errors vary by platform
            last_error = error
            if attempt < retries:
                time.sleep(attempt)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def paper_id(url: str) -> str:
    return url.rsplit("/", 1)[-1].removesuffix(".html")


def normalize_date(value: str, year: int) -> str:
    match = re.fullmatch(r"(\d{4})/(\d{2})/(\d{2})", value)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}T00:00:00Z"
    return f"{year:04d}-01-01T00:00:00Z"


def fetch_record(url: str, args: argparse.Namespace) -> dict[str, object]:
    cache_path = args.cache_dir / f"{paper_id(url)}.html"
    if cache_path.exists():
        payload = cache_path.read_bytes()
    else:
        payload = fetch(url, timeout=args.timeout, retries=args.retries)
        cache_path.write_bytes(payload)
    parser = DetailParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    title = (parser.meta.get("citation_title") or [""])[0].strip()
    authors = [value.strip() for value in parser.meta.get("citation_author", []) if value.strip()]
    published = normalize_date(
        (parser.meta.get("citation_publication_date") or [str(args.year)])[0], args.year
    )
    pdf_url = (parser.meta.get("citation_pdf_url") or [""])[0].strip().replace(
        "http://www.roboticsproceedings.org/", f"{ORIGIN}/"
    )
    if not all((title, authors, parser.abstract, pdf_url, parser.doi)):
        raise ValueError(f"incomplete RSS record {url}")
    return {
        "id": paper_id(url),
        "source_paper_id": paper_id(url),
        "doi": parser.doi,
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
    args = parse_args()
    if not re.fullmatch(r"rss\d{2}", args.series):
        raise SystemExit("--series must look like rss21")
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    index_url = f"{ORIGIN}/{args.series}/"
    index_cache = args.cache_dir / "index.html"
    if index_cache.exists():
        index = index_cache.read_bytes()
    else:
        index = fetch(index_url, timeout=args.timeout, retries=args.retries)
        index_cache.write_bytes(index)
    parser = IndexParser(args.series)
    parser.feed(index.decode("utf-8", errors="replace"))
    # Some editions use relative pNNN.html links; resolve those directly here.
    links = sorted(
        urljoin(index_url, match)
        for match in set(re.findall(r'href=["\']((?:\./)?p\d{3}\.html)["\']', index.decode("utf-8", errors="replace"), re.I))
    )
    if not links:
        raise SystemExit(f"{index_url} contains no paper detail links")
    records: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
        futures = {executor.submit(fetch_record, url, args): url for url in links}
        for future in as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda record: str(record["id"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"source={index_url}")
    print(f"record_count={len(records)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
