#!/usr/bin/env python3
"""Fill missing conference PDF URLs from exact-title OpenAlex matches.

Only HTTPS PDF URLs already accepted by aPaper's source download policy are
written. Every candidate is fetched and must begin with ``%PDF-`` before it is
added to the output JSONL. The lookup cache makes interrupted runs resumable.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import subprocess
import threading
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


OPENALEX_URL = "https://api.openalex.org/works"
USER_AGENT = "aPaper metadata publisher (https://github.com/YociLam/aPaper-Cloud)"
TRUSTED_HOSTS = {
    "aclanthology.org",
    "arxiv.org",
    "csdl-downloads.ieeecomputer.org",
    "ojs.aaai.org",
    "openaccess.thecvf.com",
    "proceedings.mlr.press",
    "proceedings.neurips.cc",
    "raw.githubusercontent.com",
    "www.computer.org",
    "www.ecva.net",
    "www.ieee-security.org",
    "www.ijcai.org",
    "www.ndss-symposium.org",
    "www.usenix.org",
}
MAX_PDF_BYTES = 64 * 1024 * 1024
_request_lock = threading.Lock()
_next_request_at = 0.0


def normalized_title(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def read_records(path: Path) -> list[dict[str, object]]:
    if path.suffix == ".zst":
        decoded = subprocess.run(
            ["zstd", "-dc", str(path)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    else:
        decoded = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in decoded.splitlines() if line.strip()]


def write_records(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")
    temporary.replace(path)


def load_cache(path: Path) -> dict[str, str | None]:
    if not path.exists():
        return {}
    content = json.loads(path.read_text(encoding="utf-8"))
    return content if isinstance(content, dict) else {}


def write_cache(path: Path, cache: dict[str, str | None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(
        json.dumps(cache, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    temporary.replace(path)


def wait_for_request_slot(requests_per_second: float) -> None:
    global _next_request_at
    interval = 1.0 / max(requests_per_second, 0.1)
    with _request_lock:
        now = time.monotonic()
        delay = max(0.0, _next_request_at - now)
        _next_request_at = max(now, _next_request_at) + interval
    if delay:
        time.sleep(delay)


def request_bytes(url: str, *, timeout: float, byte_range: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if byte_range:
        headers["Range"] = byte_range
        headers["Accept"] = "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_PDF_BYTES:
            raise ValueError("PDF exceeds aPaper's transient cache limit")
        return response.read(32 if byte_range else 2 * 1024 * 1024)


def normalized_candidate(value: object) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if host == "export.arxiv.org":
        host = "arxiv.org"
        parsed = parsed._replace(netloc=host)
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.port
        or host not in TRUSTED_HOSTS
    ):
        return None
    if host == "raw.githubusercontent.com" and not parsed.path.startswith("/mlresearch/"):
        return None
    return urlunparse(parsed)


def candidate_urls(work: dict[str, object], allowed_hosts: set[str]) -> list[str]:
    locations: list[object] = []
    best = work.get("best_oa_location")
    if isinstance(best, dict):
        locations.append(best)
    raw_locations = work.get("locations")
    if isinstance(raw_locations, list):
        locations.extend(raw_locations)
    result: list[str] = []
    for location in locations:
        if not isinstance(location, dict):
            continue
        candidate = normalized_candidate(location.get("pdf_url"))
        if (
            candidate
            and (urlparse(candidate).hostname or "").lower() in allowed_hosts
            and candidate not in result
        ):
            result.append(candidate)
    return result


def valid_pdf(url: str, *, timeout: float) -> bool:
    try:
        return request_bytes(url, timeout=timeout, byte_range="bytes=0-31").startswith(b"%PDF-")
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return False


def lookup_pdf(
    title: str,
    *,
    timeout: float,
    pdf_timeout: float,
    retries: int,
    requests_per_second: float,
    allowed_hosts: set[str],
) -> tuple[str, str | None, str]:
    key = normalized_title(title)
    query = urlencode(
        {
            "search": title,
            "per-page": 5,
            "select": "title,best_oa_location,locations",
        }
    )
    for attempt in range(retries):
        try:
            wait_for_request_slot(requests_per_second)
            payload = json.loads(request_bytes(f"{OPENALEX_URL}?{query}", timeout=timeout))
            results = payload.get("results") if isinstance(payload, dict) else None
            if not isinstance(results, list):
                return key, None, "error"
            exact = next(
                (
                    item
                    for item in results
                    if isinstance(item, dict)
                    and normalized_title(item.get("title")) == key
                ),
                None,
            )
            if exact:
                for candidate in candidate_urls(exact, allowed_hosts):
                    wait_for_request_slot(requests_per_second)
                    if valid_pdf(candidate, timeout=pdf_timeout):
                        return key, candidate, "found"
            return key, None, "missing"
        except HTTPError as error:
            if attempt + 1 < retries:
                retry_after = error.headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 3.0 * (attempt + 1)
                time.sleep(delay)
        except (URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError):
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    return key, None, "error"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--requests-per-second", type=float, default=8.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--pdf-timeout", type=float, default=12.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument(
        "--allowed-host",
        action="append",
        choices=sorted(TRUSTED_HOSTS),
        dest="allowed_hosts",
    )
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    records = read_records(args.input)
    cache = load_cache(args.cache)
    missing = [
        record
        for record in records
        if not str(record.get("pdf_url") or "").strip()
        and normalized_title(record.get("title"))
    ]
    if args.limit is not None:
        missing = missing[: max(args.limit, 0)]
    allowed_hosts = set(args.allowed_hosts or TRUSTED_HOSTS)
    pending: dict[str, str] = {}
    for record in missing:
        title = str(record.get("title") or "").strip()
        key = normalized_title(title)
        if key not in cache:
            pending.setdefault(key, title)

    completed = 0
    found = 0
    unavailable = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                lookup_pdf,
                title,
                timeout=args.timeout,
                pdf_timeout=args.pdf_timeout,
                retries=max(1, args.retries),
                requests_per_second=args.requests_per_second,
                allowed_hosts=allowed_hosts,
            ): key
            for key, title in pending.items()
        }
        for future in as_completed(futures):
            key, pdf_url, status = future.result()
            if status != "error":
                cache[key] = pdf_url
            if status == "found":
                found += 1
            elif status == "missing":
                unavailable += 1
            else:
                failed += 1
            completed += 1
            if completed % 50 == 0:
                write_cache(args.cache, cache)
                print(
                    f"lookups={completed}/{len(futures)} found={found} "
                    f"missing={unavailable} failed={failed}",
                    flush=True,
                )
    write_cache(args.cache, cache)

    updated = 0
    for record in records:
        if str(record.get("pdf_url") or "").strip():
            continue
        pdf_url = cache.get(normalized_title(record.get("title")))
        if pdf_url:
            record["pdf_url"] = pdf_url
            updated += 1
    write_records(args.output, records)
    print(
        f"records={len(records)} missing={len(missing)} updated={updated} "
        f"failed={failed}"
    )
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
