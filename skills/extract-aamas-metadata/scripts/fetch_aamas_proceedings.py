#!/usr/bin/env python3
"""Fetch one official IFAAMAS proceedings edition with verified abstracts."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
import html
import json
from pathlib import Path
import re
import time
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

import fitz


USER_AGENT = "aPaper-Cloud-Metadata/1.0 (AAMAS proceedings sync)"
PUBLISHED_DATES = {
    2025: "2025-05-19T00:00:00Z",
    2026: "2026-05-25T00:00:00Z",
}


class ContentsParser(HTMLParser):
    def __init__(self, contents_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.contents_url = contents_url
        self.records: list[dict[str, object]] = []
        self._paragraph_depth = 0
        self._paragraph_parts: list[str] = []
        self._pdf_url = ""
        self._title_parts: list[str] = []
        self._paper_link_depth = 0
        self._strong_depth = 0
        self._track = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "p":
            self._paragraph_depth += 1
            if self._paragraph_depth == 1:
                self._paragraph_parts = []
                self._pdf_url = ""
                self._title_parts = []
        if tag == "br" and self._paragraph_depth:
            self._paragraph_parts.append("\n")
        if tag == "strong":
            self._strong_depth += 1
        if tag == "a" and self._paragraph_depth:
            href = (values.get("href") or "").strip()
            if re.search(r"\.pdf$", href, re.I):
                self._pdf_url = urljoin(self.contents_url, href)
                self._paper_link_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._paper_link_depth:
            self._paper_link_depth -= 1
        if tag == "strong" and self._strong_depth:
            self._strong_depth -= 1
        if tag == "p" and self._paragraph_depth:
            self._paragraph_depth -= 1
            if self._paragraph_depth == 0:
                self._finish_paragraph()

    def handle_data(self, data: str) -> None:
        if not self._paragraph_depth:
            return
        self._paragraph_parts.append(data)
        if self._paper_link_depth:
            self._title_parts.append(data)

    def _finish_paragraph(self) -> None:
        text = "".join(self._paragraph_parts)
        normalized = " ".join(text.split())
        if not self._pdf_url:
            if normalized and self._looks_like_track(normalized):
                self._track = normalized
            return
        filename = self._pdf_url.rsplit("/", 1)[-1]
        if not re.fullmatch(r"(?:[A-Z0-9]{8}|p\d+)\.pdf", filename):
            return
        title = " ".join("".join(self._title_parts).split())
        if not title:
            return
        lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
        authors = []
        after_title = False
        for line in lines:
            if not after_title:
                if title in line:
                    after_title = True
                continue
            line = re.sub(r"^\(Page\s+\d+\)\s*", "", line, flags=re.I).strip()
            if not line or line.casefold().startswith("page "):
                continue
            name = re.split(r"\s+\(", line, maxsplit=1)[0].strip(" ,")
            if name and name not in authors:
                authors.append(name)
        self.records.append(
            {
                "id": filename.removesuffix(".pdf"),
                "title": title,
                "authors": authors,
                "pdf_url": self._pdf_url,
                "track": self._track,
            }
        )

    @staticmethod
    def _looks_like_track(text: str) -> bool:
        lowered = text.casefold()
        return any(
            token in lowered
            for token in (
                "paper track",
                "special track",
                "doctoral consortium",
                "demonstration track",
                "demo track",
                "blue sky ideas",
                "innovative applications",
                "extended abstract",
            )
        ) and len(text) < 160


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def plain_text(fragment: str) -> str:
    parser = TextParser()
    parser.feed(fragment)
    return parser.text


def parse_contents(contents: str, contents_url: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    headings = [
        (match.start(), plain_text(match.group(1)))
        for match in re.finditer(
            r"<a\b[^>]*(?:name|id)=[\"'][^\"']+[\"'][^>]*>\s*</a>\s*<font\b[^>]*>(.*?)</font>",
            contents,
            re.I | re.S,
        )
        if ContentsParser._looks_like_track(plain_text(match.group(1)))
    ]
    for paragraph in re.finditer(r"<p\b[^>]*>(.*?)</p>", contents, re.I | re.S):
        body = paragraph.group(1)
        link = re.search(
            r"<a\b[^>]*href=[\"']([^\"']+\.pdf)[\"'][^>]*>(.*?)</a>",
            body,
            re.I | re.S,
        )
        if not link:
            continue
        pdf_url = urljoin(contents_url, link.group(1).strip())
        filename = pdf_url.rsplit("/", 1)[-1]
        if not re.fullmatch(r"(?:[A-Z0-9]{8}|p\d+)\.pdf", filename):
            continue
        title = plain_text(link.group(2))
        track = next(
            (name for position, name in reversed(headings) if position < paragraph.start()),
            "",
        )
        remainder = body[link.end() :]
        author_segments = re.split(r"<br\s*/?>", remainder, flags=re.I)
        authors: list[str] = []
        for segment in author_segments[1:]:
            name = plain_text(segment.split("<i", 1)[0]).strip(" ,")
            if name and name not in authors:
                authors.append(name)
        records.append(
            {
                "id": filename.removesuffix(".pdf"),
                "title": title,
                "authors": authors,
                "pdf_url": pdf_url,
                "track": track,
            }
        )
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--retries", type=int, default=3)
    return parser.parse_args()


def fetch(url: str, *, timeout: int, retries: int, accept: str = "*/*") -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except Exception as error:  # noqa: BLE001 - URL errors vary by platform
            last_error = error
            if attempt < retries:
                time.sleep(attempt * 2)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", html.unescape(value).casefold()).strip()


def crossref_records(year: int, *, timeout: int, retries: int) -> dict[str, dict[str, str]]:
    cursor = "*"
    records: dict[str, dict[str, str]] = {}
    while cursor:
        url = (
            "https://api.crossref.org/works?"
            f"filter=from-pub-date:{year}-01-01,until-pub-date:{year}-12-31,prefix:10.65109"
            f"&rows=1000&cursor={quote(cursor)}&select=DOI,title,abstract,published"
        )
        payload = json.loads(fetch(url, timeout=timeout, retries=retries, accept="application/json"))
        message = payload["message"]
        for item in message.get("items", []):
            titles = item.get("title") or []
            abstract_html = item.get("abstract") or ""
            doi = item.get("DOI") or ""
            if not titles or not abstract_html or not doi:
                continue
            parser = TextParser()
            parser.feed(abstract_html)
            records[normalized_title(titles[0])] = {"abstract": parser.text, "doi": doi}
        next_cursor = message.get("next-cursor") or ""
        if not next_cursor or next_cursor == cursor or not message.get("items"):
            break
        cursor = next_cursor
    return records


def dehyphenate(text: str) -> str:
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=[a-z])", "", text)
    return " ".join(text.split())


def extract_pdf_metadata(path: Path, paper_id: str) -> tuple[str, str]:
    document = fitz.open(path)
    text = "\n".join(document[index].get_text() for index in range(min(2, document.page_count)))
    abstract_match = re.search(
        r"\bABSTRACT\b\s*(.+?)(?=\n\s*(?:CCS CONCEPTS|KEYWORDS|ACM Reference Format|1\s+INTRODUCTION)\b)",
        text,
        re.I | re.S,
    )
    doi_match = re.search(rf"10\.65109/{re.escape(paper_id)}\b", text, re.I)
    abstract = dehyphenate(abstract_match.group(1)) if abstract_match else ""
    doi = doi_match.group(0) if doi_match else ""
    return abstract, doi


def enrich_record(
    record: dict[str, object],
    *,
    year: int,
    crossref: dict[str, dict[str, str]],
    cache_dir: Path,
    timeout: int,
    retries: int,
) -> dict[str, object]:
    matched = crossref.get(normalized_title(str(record["title"])))
    if matched:
        abstract = matched["abstract"]
        doi = matched["doi"]
    else:
        cache_path = cache_dir / f"{record['id']}.pdf"
        if not cache_path.exists():
            cache_path.write_bytes(
                fetch(str(record["pdf_url"]), timeout=timeout, retries=retries, accept="application/pdf")
            )
        abstract, doi = extract_pdf_metadata(cache_path, str(record["id"]))
    if not abstract:
        raise ValueError(f"could not extract abstract for {record['id']} {record['title']}")
    if not record["authors"]:
        raise ValueError(f"could not extract authors for {record['id']} {record['title']}")
    source_group = None
    if record["track"]:
        source_group = {
            "id": "aamas." + re.sub(r"[^a-z0-9]+", ".", str(record["track"]).casefold()).strip("."),
            "name": record["track"],
            "kind": "track",
        }
    landing_url = f"https://doi.org/{doi}" if doi else str(record["pdf_url"])
    return {
        "id": record["id"],
        "source_paper_id": record["id"],
        "doi": doi,
        "title": record["title"],
        "abstract": abstract,
        "authors": record["authors"],
        "categories": [],
        "source_group": source_group,
        "published": PUBLISHED_DATES.get(year, f"{year:04d}-01-01T00:00:00Z"),
        "link": landing_url,
        "pdf_url": record["pdf_url"],
        "updated_at": PUBLISHED_DATES.get(year, f"{year:04d}-01-01T00:00:00Z"),
    }


def main() -> None:
    args = parse_args()
    contents_url = f"https://www.ifaamas.org/Proceedings/aamas{args.year}/forms/contents.htm"
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    contents_cache = args.cache_dir / "contents.html"
    if contents_cache.exists():
        contents = contents_cache.read_bytes()
    else:
        contents = fetch(contents_url, timeout=args.timeout, retries=args.retries, accept="text/html")
        contents_cache.write_bytes(contents)
    official_records = parse_contents(contents.decode("windows-1252", errors="replace"), contents_url)
    if not official_records:
        raise SystemExit(f"{contents_url} contains no AAMAS paper records")
    crossref = crossref_records(args.year, timeout=args.timeout, retries=args.retries)
    records: list[dict[str, object]] = []
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as executor:
        futures = {
            executor.submit(
                enrich_record,
                record,
                year=args.year,
                crossref=crossref,
                cache_dir=args.cache_dir,
                timeout=args.timeout,
                retries=args.retries,
            ): record
            for record in official_records
        }
        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as error:  # noqa: BLE001 - report every publisher-record failure
                failures.append(f"{futures[future]['id']}: {error}")
    records.sort(key=lambda record: str(record["id"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"source={contents_url}")
    print(f"official_paper_count={len(official_records)}")
    print(f"crossref_abstract_count={len(crossref)}")
    print(f"record_count={len(records)}")
    print(f"failure_count={len(failures)}")
    for failure in failures[:20]:
        print(f"failure={failure}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
