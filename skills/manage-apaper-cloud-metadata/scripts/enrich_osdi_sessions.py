#!/usr/bin/env python3
"""Enrich OSDI JSONL records with official technical-session names."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class OSDISessionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_session: str | None = None
        self.sessions_by_path: dict[str, str] = {}
        self.in_h2 = False
        self.h2_text: list[str] = []
        self.h2_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "h2":
            self.in_h2 = True
            self.h2_text = []
            self.h2_href = None
        elif tag.lower() == "a" and self.in_h2:
            values = {key.lower(): value for key, value in attrs if value is not None}
            self.h2_href = values.get("href")

    def handle_data(self, data: str) -> None:
        if self.in_h2:
            self.h2_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "h2" or not self.in_h2:
            return
        text = " ".join("".join(self.h2_text).split())
        href = self.h2_href
        self.in_h2 = False
        if href and re.fullmatch(r"/conference/osdi\d+/presentation/[^/?#]+", href):
            if self.current_session:
                self.sessions_by_path[href.rstrip("/")] = self.current_session
        elif text:
            self.current_session = text


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Attach official OSDI technical-session names to JSONL records."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--year", required=True, type=int)
    return parser.parse_args()


def fetch_program(year: int) -> tuple[str, dict[str, str]]:
    short_year = year % 100
    url = f"https://www.usenix.org/conference/osdi{short_year}/technical-sessions"
    request = urllib.request.Request(
        url,
        headers={
            "Accept-Encoding": "gzip",
            "User-Agent": "aPaper-Cloud-Metadata/1.0 (OSDI session sync)",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        body = response.read()
        if response.headers.get("Content-Encoding", "").lower() == "gzip":
            body = gzip.decompress(body)
    parser = OSDISessionParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    return url, parser.sessions_by_path


def stable_session_id(session: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", session.lower()).strip("-")
    return f"osdi.session.{slug[:108]}"


def main() -> None:
    arguments = parse_arguments()
    program_url, sessions = fetch_program(arguments.year)
    records = [
        json.loads(line)
        for line in arguments.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    missing: list[str] = []
    for record in records:
        if record.get("venue_id") != "osdi" or record.get("year") != arguments.year:
            raise SystemExit("input contains a record outside the requested OSDI edition")
        path = urllib.parse.urlparse(record["landing_url"]).path.rstrip("/")
        session = sessions.get(path)
        if not session:
            missing.append(record["landing_url"])
            continue
        record["categories"] = [session]
        record["source_group"] = {
            "id": stable_session_id(session),
            "name": session,
            "kind": "program_session",
        }
        record["provenance_url"] = record.get("provenance_url") or program_url

    if missing:
        for value in missing[:20]:
            print(f"missing session: {value}")
        raise SystemExit(f"OSDI session sync missed {len(missing)} of {len(records)} records")

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")
    print(f"mapped={len(records)} sessions={len(set(sessions.values()))}")


if __name__ == "__main__":
    main()
