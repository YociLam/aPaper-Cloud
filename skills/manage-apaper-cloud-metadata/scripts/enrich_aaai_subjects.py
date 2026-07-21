#!/usr/bin/env python3
"""Enrich AAAI JSONL records with source-native OJS subject metadata."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path


class SubjectMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.subjects: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        values = {key.lower(): value for key, value in attrs if value is not None}
        if values.get("name", "").lower() != "dc.subject":
            return
        subject = " ".join(values.get("content", "").split())
        if subject and subject not in self.subjects:
            self.subjects.append(subject)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch official AAAI OJS subject metadata for a JSONL pack."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=12)
    return parser.parse_args()


def fetch_subjects(url: str, cache_dir: Path) -> list[str]:
    cache_path = cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
    if cache_path.is_file():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(cached, list) and all(isinstance(value, str) for value in cached):
            return cached

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "Accept-Encoding": "gzip",
                    "User-Agent": "aPaper-Cloud-Metadata/1.0 (AAAI subject sync)",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                if response.headers.get("Content-Encoding", "").lower() == "gzip":
                    body = gzip.decompress(body)
            parser = SubjectMetaParser()
            parser.feed(body.decode("utf-8", errors="replace"))
            if not parser.subjects:
                raise ValueError("official article page did not contain DC.Subject metadata")
            cache_path.write_text(
                json.dumps(parser.subjects, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return parser.subjects
        except Exception as error:  # urllib exposes several transport error types.
            last_error = error
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"could not fetch {url}: {last_error}")


def stable_subject_id(subject: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
    return f"aaai.subject.{slug[:108]}"


def main() -> None:
    arguments = parse_arguments()
    if arguments.workers < 1 or arguments.workers > 32:
        raise SystemExit("--workers must be between 1 and 32")
    arguments.cache_dir.mkdir(parents=True, exist_ok=True)
    records = [
        json.loads(line)
        for line in arguments.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if any(record.get("venue_id") != "aaai" for record in records):
        raise SystemExit("input contains a non-AAAI record")

    subjects_by_index: dict[int, list[str]] = {}
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=arguments.workers) as executor:
        futures = {
            executor.submit(
                fetch_subjects,
                record["provenance_url"],
                arguments.cache_dir,
            ): index
            for index, record in enumerate(records)
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            index = futures[future]
            try:
                subjects_by_index[index] = future.result()
            except Exception as error:
                failures.append(str(error))
            if completed % 100 == 0 or completed == len(futures):
                print(
                    f"processed={completed}/{len(futures)} failures={len(failures)}",
                    flush=True,
                )

    if failures:
        for failure in failures[:20]:
            print(failure)
        raise SystemExit(f"AAAI subject sync failed for {len(failures)} records")

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", encoding="utf-8") as output:
        for index, record in enumerate(records):
            subjects = subjects_by_index[index]
            record["categories"] = subjects
            if not record.get("source_group"):
                primary = subjects[0]
                record["source_group"] = {
                    "id": stable_subject_id(primary),
                    "name": primary,
                    "kind": "subject_area",
                }
            output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")


if __name__ == "__main__":
    main()
