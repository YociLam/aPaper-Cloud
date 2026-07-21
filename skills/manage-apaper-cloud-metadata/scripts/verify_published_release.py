#!/usr/bin/env python3
"""Verify that aPaper Cloud serves the exact local metadata release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen


VERSION_PATH = "v1/conferences/version.json"
MANIFEST_PATH = "v1/conferences/manifest.json"
MAX_VERSION_BYTES = 16 * 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_PACK_BYTES = 128 * 1024 * 1024
USER_AGENT = "aPaper metadata release verifier (https://cloud.apaper.ai)"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bounded(response, limit: int, label: str) -> bytes:
    data = response.read(limit + 1)
    if len(data) > limit:
        raise RuntimeError(f"{label} exceeds {limit} bytes")
    return data


def fetch(origin: str, path: str, limit: int, timeout: float) -> bytes:
    url = urljoin(origin.rstrip("/") + "/", path)
    separator = "&" if "?" in url else "?"
    url = f"{url}{separator}release-check={time.time_ns()}"
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/octet-stream",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"GET {url} returned HTTP {status}")
        return read_bounded(response, limit, url)


def load_json(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{label} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return value


def edition_pack(manifest: dict, edition_id: str) -> dict:
    for venue in manifest.get("venues", []):
        for edition in venue.get("editions", []):
            if edition.get("id") == edition_id:
                pack = edition.get("pack")
                if not isinstance(pack, dict):
                    raise RuntimeError(f"{edition_id} has no published pack")
                return pack
    raise RuntimeError(f"edition not found in manifest: {edition_id}")


def verify_pack(
    public: Path,
    origin: str,
    manifest: dict,
    edition_id: str,
    timeout: float,
) -> None:
    pack = edition_pack(manifest, edition_id)
    relative_path = str(pack["path"])
    expected_bytes = int(pack["compressed_bytes"])
    expected_sha = str(pack["sha256"])
    local_path = public / "v1" / "conferences" / relative_path
    local_data = local_path.read_bytes()
    if len(local_data) != expected_bytes or sha256(local_data) != expected_sha:
        raise RuntimeError(f"local pack does not match manifest: {edition_id}")
    remote_data = fetch(
        origin,
        f"v1/conferences/{relative_path}",
        MAX_PACK_BYTES,
        timeout,
    )
    if len(remote_data) != expected_bytes:
        raise RuntimeError(
            f"remote pack byte count mismatch for {edition_id}: "
            f"expected {expected_bytes}, got {len(remote_data)}"
        )
    remote_sha = sha256(remote_data)
    if remote_sha != expected_sha:
        raise RuntimeError(
            f"remote pack SHA-256 mismatch for {edition_id}: "
            f"expected {expected_sha}, got {remote_sha}"
        )
    print(f"verified pack {edition_id}: {expected_bytes} bytes, sha256={expected_sha}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, default=Path("public"))
    parser.add_argument("--origin", help="Override manifest canonical_origin")
    parser.add_argument(
        "--pack",
        action="append",
        default=[],
        metavar="VENUE:YEAR",
        help="Verify a changed edition pack; repeat for every changed pack",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--allow-origin-mismatch",
        action="store_true",
        help="Allow a non-canonical origin only for local release-verifier tests",
    )
    args = parser.parse_args()

    conference_root = args.public / "v1" / "conferences"
    local_manifest_data = (conference_root / "manifest.json").read_bytes()
    local_version_data = (conference_root / "version.json").read_bytes()
    local_manifest = load_json(local_manifest_data, "local manifest")
    local_version = load_json(local_version_data, "local version")
    local_manifest_sha = sha256(local_manifest_data)
    if local_version.get("manifest_sha256") != local_manifest_sha:
        raise RuntimeError("local version.json does not match local manifest SHA-256")
    if local_version.get("manifest_version") != local_manifest.get("manifest_version"):
        raise RuntimeError("local version.json does not match local manifest version")
    if local_version.get("updated_at") != local_manifest.get("generated_at"):
        raise RuntimeError("local version.json updated_at does not match manifest generated_at")

    origin = args.origin or str(local_manifest.get("canonical_origin", ""))
    if not origin:
        raise RuntimeError("no origin supplied and canonical_origin is missing")

    remote_version_data = fetch(origin, VERSION_PATH, MAX_VERSION_BYTES, args.timeout)
    remote_version = load_json(remote_version_data, "remote version")
    for field in (
        "schema_version",
        "dataset",
        "manifest_version",
        "updated_at",
        "manifest_sha256",
    ):
        if remote_version.get(field) != local_version.get(field):
            raise RuntimeError(
                f"remote version field {field} does not match local release: "
                f"expected {local_version.get(field)!r}, got {remote_version.get(field)!r}"
            )

    remote_manifest_data = fetch(origin, MANIFEST_PATH, MAX_MANIFEST_BYTES, args.timeout)
    remote_manifest_sha = sha256(remote_manifest_data)
    if remote_manifest_sha != local_manifest_sha:
        raise RuntimeError(
            "remote manifest SHA-256 does not match local release: "
            f"expected {local_manifest_sha}, got {remote_manifest_sha}"
        )
    remote_manifest = load_json(remote_manifest_data, "remote manifest")
    if (
        not args.allow_origin_mismatch
        and remote_manifest.get("canonical_origin") != origin.rstrip("/")
    ):
        raise RuntimeError("remote manifest canonical_origin does not match verified origin")

    print(
        "verified release control plane: "
        f"manifest_version={local_version['manifest_version']}, "
        f"sha256={local_manifest_sha}"
    )
    for edition_id in dict.fromkeys(args.pack):
        verify_pack(args.public, origin, local_manifest, edition_id, args.timeout)


if __name__ == "__main__":
    main()
