#!/usr/bin/env python3
"""Fetch one final PMLR volume from its publisher-maintained GitHub branch."""

from __future__ import annotations

import argparse
import io
import json
import re
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path


USER_AGENT = "aPaper-Cloud-Metadata/1.0 (PMLR volume importer)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", required=True, help="PMLR volume, for example v258")
    parser.add_argument("--venue", required=True)
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--expected-title-fragment", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def download(url: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(3):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"could not download {url}: {last_error}")


def yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    return value


def frontmatter(markdown: str) -> list[str]:
    normalized = markdown.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = normalized.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    return normalized[4:end].splitlines()


def scalar(lines: list[str], key: str) -> str:
    prefix = f"{key}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        parts = [line[len(prefix) :].strip()]
        next_index = index + 1
        while next_index < len(lines):
            continuation = lines[next_index]
            if continuation and not continuation[0].isspace():
                break
            if continuation.strip():
                parts.append(continuation.strip())
            next_index += 1
        return " ".join(yaml_scalar(part) for part in parts if part).strip()
    return ""


def authors(lines: list[str]) -> list[str]:
    try:
        start = lines.index("author:") + 1
    except ValueError:
        return []
    values: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines[start:]:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line):
            break
        item = re.match(r"^\s*-\s+(given|family|literal):\s*(.*)$", line)
        field = re.match(r"^\s+(given|family|literal):\s*(.*)$", line)
        if item:
            if current:
                values.append(current)
            current = {item.group(1): yaml_scalar(item.group(2))}
        elif field and current is not None:
            current[field.group(1)] = yaml_scalar(field.group(2))
    if current:
        values.append(current)
    normalized = []
    for value in values:
        name = value.get("literal") or " ".join(
            part for part in (value.get("given", ""), value.get("family", "")) if part
        )
        if name.strip():
            normalized.append(" ".join(name.split()))
    return normalized


def iso_date(value: str, year: int) -> str:
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
    if match:
        return f"{value}T00:00:00Z"
    return f"{year:04d}-01-01T00:00:00Z"


def parse_record(
    markdown: str,
    *,
    volume: str,
    venue: str,
    year: int,
    expected_title_fragment: str,
) -> dict[str, object] | None:
    lines = frontmatter(markdown)
    paper_id = scalar(lines, "id")
    title = scalar(lines, "title")
    abstract = scalar(lines, "abstract")
    paper_authors = authors(lines)
    container_title = scalar(lines, "container-title")
    pdf_url = scalar(lines, "pdf")
    doi = scalar(lines, "doi")
    section = scalar(lines, "section")
    published = iso_date(scalar(lines, "date"), year)
    if expected_title_fragment.casefold() not in container_title.casefold():
        raise ValueError(f"unexpected container title for {paper_id}: {container_title}")
    if not abstract and section.casefold() == "preface":
        return None
    if not all((paper_id, title, abstract, paper_authors, pdf_url)):
        raise ValueError(f"incomplete PMLR record {paper_id or '<unknown>'}")
    landing_url = f"https://proceedings.mlr.press/{volume}/{paper_id}.html"
    return {
        "id": paper_id,
        "source_paper_id": paper_id,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "authors": paper_authors,
        "categories": [],
        "published": published,
        "link": landing_url,
        "pdf_url": pdf_url,
        "updated_at": published,
    }


def main() -> None:
    args = parse_args()
    if not re.fullmatch(r"v\d+", args.volume):
        raise SystemExit("--volume must look like v258")
    archive_url = (
        f"https://codeload.github.com/mlresearch/{args.volume}/tar.gz/refs/heads/gh-pages"
    )
    payload = download(archive_url)
    records = []
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        posts = sorted(
            [
                member
                for member in archive.getmembers()
                if member.isfile()
                and "/_posts/" in member.name
                and member.name.endswith(".md")
            ],
            key=lambda member: member.name,
        )
        if not posts:
            raise SystemExit(f"{args.volume} has no final gh-pages metadata posts")
        for member in posts:
            source = archive.extractfile(member)
            if source is None:
                raise SystemExit(f"could not read {member.name}")
            record = parse_record(
                source.read().decode("utf-8"),
                volume=args.volume,
                venue=args.venue,
                year=args.year,
                expected_title_fragment=args.expected_title_fragment,
            )
            if record is not None:
                records.append(record)
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{args.volume} contains duplicate paper IDs")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"volume={args.volume}")
    print(f"record_count={len(records)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
