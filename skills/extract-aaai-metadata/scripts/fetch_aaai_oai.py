#!/usr/bin/env python3
"""Fetch one AAAI proceedings year from the official OJS OAI-PMH endpoint."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


BASE_URL = "https://ojs.aaai.org/index.php/AAAI/oai"
OAI_NS = "http://www.openarchives.org/OAI/2.0/"
DC_NS = "http://purl.org/dc/elements/1.1/"
USER_AGENT = "aPaper-Cloud-Metadata/1.0 (AAAI OAI-PMH sync)"


def request_xml(parameters: dict[str, str], retries: int = 8) -> ET.Element:
    url = f"{BASE_URL}?{urllib.parse.urlencode(parameters)}"
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"Accept-Encoding": "identity", "User-Agent": USER_AGENT},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                return ET.fromstring(response.read())
        except Exception as error:  # noqa: BLE001 - network failures vary
            last_error = error
            if attempt < retries:
                time.sleep(min(attempt * 5, 30))
    raise RuntimeError(f"AAAI OAI request failed: {url}: {last_error}")


def oai_pages(parameters: dict[str, str], cache_dir: Path, prefix: str):
    current = parameters
    page = 1
    while True:
        cache_path = cache_dir / f"{prefix}-{page:04d}.xml"
        if cache_path.exists():
            root = ET.fromstring(cache_path.read_bytes())
        else:
            root = request_xml(current)
            cache_path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
        yield root
        token = root.findtext(f".//{{{OAI_NS}}}resumptionToken", default="").strip()
        if not token:
            return
        current = {"verb": parameters["verb"], "resumptionToken": token}
        page += 1


def fetch_sets(cache_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for root in oai_pages({"verb": "ListSets"}, cache_dir, "sets"):
        for node in root.findall(f".//{{{OAI_NS}}}set"):
            spec = node.findtext(f"{{{OAI_NS}}}setSpec", default="").strip()
            name = node.findtext(f"{{{OAI_NS}}}setName", default="").strip()
            if spec and name:
                result[spec] = name
    return result


def text_values(node: ET.Element, name: str) -> list[str]:
    return [
        " ".join((child.text or "").split())
        for child in node.findall(f".//{{{DC_NS}}}{name}")
        if (child.text or "").strip()
    ]


def normalize_author(value: str) -> str:
    if "," not in value:
        return value
    family, given = value.split(",", 1)
    return " ".join(f"{given.strip()} {family.strip()}".split())


def stable_group_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:128]


def normalize_pdf_url(value: str) -> str:
    return re.sub(r"/article/view/(\d+)/(\d+)$", r"/article/download/\1/\2", value)


def parse_record(
    record: ET.Element,
    *,
    year: int,
    volume: int,
    set_names: dict[str, str],
) -> dict[str, object] | None:
    header = record.find(f"{{{OAI_NS}}}header")
    metadata = record.find(f"{{{OAI_NS}}}metadata")
    if header is None or metadata is None or header.get("status") == "deleted":
        return None
    sources = text_values(metadata, "source")
    proceedings_source = next(
        (
            value
            for value in sources
            if f"Vol. {volume} No." in value and f"AAAI-{year % 100:02d}" in value
        ),
        None,
    )
    if proceedings_source is None:
        return None
    titles = text_values(metadata, "title")
    descriptions = text_values(metadata, "description")
    identifiers = text_values(metadata, "identifier")
    relations = text_values(metadata, "relation")
    dates = text_values(metadata, "date")
    if not titles or not descriptions:
        return None
    landing_url = next(
        (value for value in identifiers if "/AAAI/article/view/" in value), ""
    )
    match = re.search(r"/article/view/(\d+)", landing_url)
    if not landing_url or match is None:
        return None
    doi = next((value for value in identifiers if value.startswith("10.")), None)
    pdf_url = next(
        (
            normalize_pdf_url(value)
            for value in relations
            if "/AAAI/article/" in value
        ),
        "",
    )
    set_specs = [
        (node.text or "").strip()
        for node in header.findall(f"{{{OAI_NS}}}setSpec")
        if (node.text or "").strip()
    ]
    group_name = next(
        (
            set_names[spec]
            for spec in set_specs
            if spec in set_names and set_names[spec].startswith("AAAI ")
        ),
        "",
    )
    if not group_name.startswith("AAAI Technical Track"):
        return None
    subjects = text_values(metadata, "subject")
    categories = subjects
    source_group = None
    if group_name:
        source_group = {
            "id": stable_group_id(group_name),
            "name": group_name,
            "kind": "track",
        }
    published = f"{dates[0]}T00:00:00Z" if dates else f"{year:04d}-01-01T00:00:00Z"
    return {
        "id": match.group(1),
        "title": titles[0],
        "abstract": descriptions[0],
        "authors": [normalize_author(value) for value in text_values(metadata, "creator")],
        "published": published,
        "updated_at": published,
        "link": landing_url,
        "pdf_url": pdf_url,
        "doi": doi,
        "categories": categories,
        "source_group": source_group,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/apaper-aaai-oai"))
    args = parser.parse_args()
    volume = args.year - 1986
    if volume <= 0:
        raise SystemExit("unsupported AAAI year")
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    set_names = fetch_sets(args.cache_dir)
    records: dict[str, dict[str, object]] = {}
    set_prefix = f"AAAI:AI{args.year % 100:02d}-"
    edition_sets = sorted(spec for spec in set_names if spec.startswith(set_prefix))
    if not edition_sets:
        raise SystemExit(f"AAAI OAI exposed no sets matching {set_prefix}")
    for index, set_spec in enumerate(edition_sets, start=1):
        parameters = {
            "verb": "ListRecords",
            "metadataPrefix": "oai_dc",
            "set": set_spec,
        }
        cache_prefix = f"records-{args.year}-{set_spec.replace(':', '-') }"
        for root in oai_pages(parameters, args.cache_dir, cache_prefix):
            for node in root.findall(f".//{{{OAI_NS}}}record"):
                record = parse_record(
                    node,
                    year=args.year,
                    volume=volume,
                    set_names=set_names,
                )
                if record is not None:
                    records[str(record["id"])] = record
        print(
            f"sets={index}/{len(edition_sets)} set={set_spec} records={len(records)}",
            flush=True,
        )
    ordered = sorted(records.values(), key=lambda record: int(str(record["id"])))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote={len(ordered)} output={args.output}")


if __name__ == "__main__":
    main()
