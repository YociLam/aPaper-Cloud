#!/usr/bin/env python3

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronize conference version.json with manifest.json."
    )
    parser.add_argument("public_root", type=Path)
    args = parser.parse_args()

    conference_root = args.public_root / "v1" / "conferences"
    manifest_path = conference_root / "manifest.json"
    version_path = conference_root / "version.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    version = {
        "schema_version": manifest["schema_version"],
        "dataset": manifest["dataset"],
        "manifest_version": manifest["manifest_version"],
        "updated_at": manifest["generated_at"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    version_path.write_text(
        json.dumps(version, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
