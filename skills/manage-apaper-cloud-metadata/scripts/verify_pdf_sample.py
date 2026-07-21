#!/usr/bin/env python3
"""Verify a deterministic sample of conference-pack PDF URLs."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import time
from urllib.request import Request, urlopen


USER_AGENT = "aPaper-Cloud-Metadata/1.0 (PDF sample verification)"


def load_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def stable_sample(records: list[dict[str, object]], fraction: float) -> list[dict[str, object]]:
    count = max(1, math.ceil(len(records) * fraction))
    return sorted(
        records,
        key=lambda record: hashlib.sha256(str(record.get("id", "")).encode()).digest(),
    )[:count]


def verify(record: dict[str, object], timeout: int, retries: int) -> tuple[str, str]:
    paper_id = str(record.get("id", ""))
    url = str(record.get("pdf_url", ""))
    if not url.startswith("https://"):
        return paper_id, "missing or non-HTTPS PDF URL"
    last_error = "unknown error"
    for attempt in range(1, retries + 1):
        try:
            request = Request(
                url,
                headers={"User-Agent": USER_AGENT, "Range": "bytes=0-31"},
            )
            with urlopen(request, timeout=timeout) as response:
                prefix = response.read(5)
                if response.status not in (200, 206):
                    raise RuntimeError(f"HTTP {response.status}")
                if prefix != b"%PDF-":
                    raise RuntimeError(f"invalid PDF header {prefix!r}")
                return paper_id, ""
        except Exception as error:  # noqa: BLE001 - network errors vary by source
            last_error = str(error)
            if attempt < retries:
                time.sleep(attempt)
    return paper_id, last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--fraction", type=float, default=0.05)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()
    if not 0 < args.fraction <= 1:
        raise SystemExit("fraction must be greater than 0 and at most 1")

    records = load_records(args.input)
    sample = stable_sample(records, args.fraction)
    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(args.workers, 1)) as executor:
        futures = {
            executor.submit(verify, record, args.timeout, max(args.retries, 1)): record
            for record in sample
        }
        for future in as_completed(futures):
            paper_id, error = future.result()
            if error:
                failures.append((paper_id, error))

    print(f"records={len(records)}")
    print(f"sampled={len(sample)}")
    print(f"verified={len(sample) - len(failures)}")
    print(f"failed={len(failures)}")
    for paper_id, error in failures[:20]:
        print(f"failure id={paper_id} error={error}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
