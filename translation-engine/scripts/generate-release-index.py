#!/usr/bin/env python3
"""Generate the small public index for immutable Translation Engine assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SHARED_FIELDS = (
    "schema_version",
    "engine_version",
    "backend",
    "worker_protocol_version",
    "minimum_macos_version",
    "python_version",
    "python_build_release",
    "pdfmathtranslate_version",
    "pdfmathtranslate_upstream_commit",
    "pdfmathtranslate_commitment",
    "dependency_lock_commitment",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def committed_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"release input unavailable: {path}")
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--arm64-metadata", type=Path, required=True)
    parser.add_argument("--x86-64-metadata", type=Path, required=True)
    parser.add_argument("--environment-definition", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    metadata_paths = [arguments.arm64_metadata, arguments.x86_64_metadata]
    metadata = [json.loads(path.read_text("utf-8")) for path in metadata_paths]
    first = metadata[0]
    for other in metadata[1:]:
        if any(other.get(field) != first.get(field) for field in SHARED_FIELDS):
            raise RuntimeError("architecture release metadata is incompatible")
    if [entry.get("architecture") for entry in metadata] != ["arm64", "x86_64"]:
        raise RuntimeError("architecture release metadata order is invalid")

    assets = []
    for path, entry in zip(metadata_paths, metadata):
        package = entry.get("assets")
        if not isinstance(package, list) or len(package) != 1:
            raise RuntimeError("architecture package metadata is invalid")
        package = package[0]
        architecture = entry["architecture"]
        name = package["name"]
        assets.append(
            {
                "architecture": architecture,
                "minimum_macos_version": entry["minimum_macos_version"],
                "compressed_size": package["bytes"],
                "installed_size": entry["installed_size"],
                "package": {
                    **package,
                    "cloud_url": (
                        f"https://cloud.apaper.ai/v1/translation/{entry['engine_version']}"
                        f"/assets/macos/{architecture}/{name}"
                    ),
                    "github_release_url": (
                        "https://github.com/YociLam/aPaper-Cloud/releases/download/"
                        f"{arguments.release_tag}/{name}"
                    ),
                },
                "file_inventory": {
                    **committed_file(path),
                    "file_count": len(entry["files"]),
                    "github_release_url": (
                        "https://github.com/YociLam/aPaper-Cloud/releases/download/"
                        f"{arguments.release_tag}/{path.name}"
                    ),
                },
            }
        )

    output = {
        **{field: first[field] for field in SHARED_FIELDS},
        "release_tag": arguments.release_tag,
        "environment_definition": committed_file(arguments.environment_definition),
        "bundled_source_archive": committed_file(arguments.source_archive),
        "assets": assets,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "utf-8",
    )
    print(json.dumps(committed_file(arguments.output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
