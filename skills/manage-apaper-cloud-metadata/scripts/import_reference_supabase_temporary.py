#!/usr/bin/env python3
"""Import one conference edition from the reference project's public Supabase.

TEMPORARY_REFERENCE_SUPABASE_CHANNEL

This is a removable bridge, not a production source. It converts the reference
project's accepted-paper rows into aPaper's static conference JSONL contract.
The macOS app never connects to Supabase; it continues to consume immutable
aPaper Cloud packs.

PDF policy: the bridge does not copy OpenReview or ACM PDF URLs because those
hosts currently return browser challenge pages to aPaper's downloader. It only
preserves PDF URLs already present in an existing, previously validated pack.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlparse

import requests
import yaml


CHANNEL_ID = "temporary_reference_supabase_v1"
PAGE_SIZE = 1_000
SOURCE_SPECS = {
    "iclr": {
        "table": "iclr_openreview_papers",
        "source": "ICLR-{year}-Accepted",
    },
    "sosp": {
        "table": "sosp_papers",
        "source": "SOSP-{year}-ACM",
    },
}


def collapse(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_abstract(value: object) -> str:
    words = collapse(value).split()
    if len(words) % 2 == 0:
        midpoint = len(words) // 2
        if words[:midpoint] == words[midpoint:]:
            words = words[:midpoint]
    return " ".join(words)


def normalized_title(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", collapse(value).lower())


def normalize_timestamp(value: object, year: int) -> str:
    raw = collapse(value)
    if not raw:
        return f"{year:04d}-01-01T00:00:00Z"
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return raw
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_authors(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    authors: list[str] = []
    for item in value:
        if isinstance(item, str):
            name = collapse(item)
        elif isinstance(item, dict):
            name = collapse(item.get("name") or item.get("full_name"))
        else:
            name = ""
        if name:
            authors.append(name)
    return authors


def openreview_id(url: object) -> str:
    parsed = urlparse(collapse(url))
    return collapse(parse_qs(parsed.query).get("id", [""])[0])


def doi_from_row(row: dict[str, Any]) -> str | None:
    doi = collapse(row.get("doi"))
    if doi:
        return doi.removeprefix("https://doi.org/")
    link = collapse(row.get("link"))
    marker = "/doi/"
    if marker in link:
        return link.split(marker, 1)[1].split("?", 1)[0].strip("/") or None
    return None


def source_categories(row: dict[str, Any], venue: str, year: int) -> list[str]:
    raw: list[str] = []
    primary = collapse(row.get("primary_category"))
    if primary:
        raw.append(primary)
    values = row.get("categories")
    if isinstance(values, list):
        raw.extend(collapse(value) for value in values)

    defaults = {
        venue.lower(),
        f"{venue.lower()}:{year}",
        f"{venue.lower()}-{year}",
    }
    if venue == "sosp":
        defaults.add("systems")

    result: list[str] = []
    seen: set[str] = set()
    for category in raw:
        key = category.casefold()
        if not category or key in defaults or key in seen:
            continue
        seen.add(key)
        result.append(category)
    return result


def load_reference_config(reference_project: Path) -> tuple[str, str, str]:
    config_path = reference_project / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    shared = config.get("supabase") or {}
    url = collapse(shared.get("url")).rstrip("/")
    anon_key = collapse(shared.get("anon_key"))
    schema = collapse(shared.get("schema")) or "public"
    if not url or not anon_key:
        raise RuntimeError(f"reference Supabase is not configured in {config_path}")
    return url, anon_key, schema


def fetch_rows(
    *,
    url: str,
    anon_key: str,
    schema: str,
    table: str,
    source: str,
) -> list[dict[str, Any]]:
    endpoint = f"{url}/rest/v1/{table}"
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Accept-Profile": schema,
    }
    select = (
        "id,source,source_paper_id,doi,version,title,abstract,authors,"
        "primary_category,categories,published,link,pdf_url,updated_at"
    )
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        response = requests.get(
            endpoint,
            headers={**headers, "Range": f"{offset}-{offset + PAGE_SIZE - 1}"},
            params={"select": select, "source": f"eq.{source}"},
            timeout=60,
        )
        response.raise_for_status()
        batch = response.json()
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected response for {table}: expected a JSON array")
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            return rows
        offset += PAGE_SIZE


def load_existing_pack(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    decoded = subprocess.run(
        ["zstd", "-dc", str(path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [json.loads(line) for line in decoded.splitlines() if line.strip()]


def build_existing_indexes(
    records: Iterable[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_forum: dict[str, dict[str, Any]] = {}
    by_doi: dict[str, dict[str, Any]] = {}
    by_title: dict[str, dict[str, Any]] = {}
    for record in records:
        forum_id = openreview_id(record.get("landing_url"))
        doi = collapse(record.get("doi")).casefold()
        title = normalized_title(record.get("title"))
        if forum_id:
            by_forum[forum_id.casefold()] = record
        if doi:
            by_doi[doi] = record
        if title:
            by_title[title] = record
    return by_forum, by_doi, by_title


def matching_existing(
    row: dict[str, Any],
    indexes: tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]],
) -> dict[str, Any] | None:
    by_forum, by_doi, by_title = indexes
    forum_id = openreview_id(row.get("link"))
    doi = (doi_from_row(row) or "").casefold()
    title = normalized_title(row.get("title"))
    return (
        (by_forum.get(forum_id.casefold()) if forum_id else None)
        or (by_doi.get(doi) if doi else None)
        or (by_title.get(title) if title else None)
    )


def record_id(row: dict[str, Any], venue: str) -> str:
    if venue == "iclr":
        forum_id = openreview_id(row.get("link"))
        if forum_id:
            return forum_id
    return collapse(row.get("source_paper_id") or row.get("id"))


def convert_rows(
    *,
    rows: list[dict[str, Any]],
    venue: str,
    year: int,
    existing: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int]:
    indexes = build_existing_indexes(existing)
    converted: list[dict[str, Any]] = []
    skipped_incomplete = 0
    preserved_pdf_count = 0
    seen_ids: set[str] = set()

    for row in rows:
        paper_id = record_id(row, venue)
        title = collapse(row.get("title"))
        abstract = normalize_abstract(row.get("abstract"))
        authors = normalize_authors(row.get("authors"))
        landing_url = collapse(row.get("link"))
        if not paper_id or not title or not abstract or not authors or not landing_url:
            skipped_incomplete += 1
            continue
        if paper_id.casefold() in seen_ids:
            raise RuntimeError(f"duplicate {venue}:{year} paper id: {paper_id}")
        seen_ids.add(paper_id.casefold())

        prior = matching_existing(row, indexes)
        pdf_url = collapse((prior or {}).get("pdf_url")) or None
        source_group = (prior or {}).get("source_group")
        if pdf_url:
            preserved_pdf_count += 1

        published_at = normalize_timestamp(row.get("published"), year)
        updated_at = normalize_timestamp(row.get("updated_at") or row.get("published"), year)
        record: dict[str, Any] = {
            "schema_version": 1,
            "id": paper_id,
            "venue_id": venue,
            "edition_id": f"{venue}:{year}",
            "year": year,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "landing_url": landing_url,
            "pdf_url": pdf_url,
            "doi": doi_from_row(row),
            "categories": source_categories(row, venue, year),
            "published_at": published_at,
            "updated_at": updated_at,
            "acceptance_status": "published",
            "provenance_url": landing_url,
            "metadata_channel": CHANNEL_ID,
        }
        if isinstance(source_group, dict):
            record["source_group"] = source_group
        converted.append(record)

    converted.sort(key=lambda item: item["id"].casefold())
    return converted, skipped_incomplete, preserved_pdf_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-project", type=Path, required=True)
    parser.add_argument("--venue", choices=sorted(SOURCE_SPECS), required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--existing-pack", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    spec = SOURCE_SPECS[args.venue]
    source = spec["source"].format(year=args.year)
    url, anon_key, schema = load_reference_config(args.reference_project)
    rows = fetch_rows(
        url=url,
        anon_key=anon_key,
        schema=schema,
        table=spec["table"],
        source=source,
    )
    if not rows:
        raise RuntimeError(f"temporary source returned no rows for {source}")

    existing = load_existing_pack(args.existing_pack)
    records, skipped, preserved_pdfs = convert_rows(
        rows=rows,
        venue=args.venue,
        year=args.year,
        existing=existing,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")

    print(f"metadata_channel={CHANNEL_ID}")
    print(f"source={source}")
    print(f"source_rows={len(rows)}")
    print(f"record_count={len(records)}")
    print(f"skipped_incomplete={skipped}")
    print(f"preserved_validated_pdfs={preserved_pdfs}")


if __name__ == "__main__":
    main()
