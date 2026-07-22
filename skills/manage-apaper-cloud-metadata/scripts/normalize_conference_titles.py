#!/usr/bin/env python3

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def command_output(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout


def output_value(output: str, name: str) -> int:
    prefix = f"{name}="
    for line in output.splitlines():
        if line.startswith(prefix):
            return int(line.removeprefix(prefix))
    raise RuntimeError(f"pack output did not contain {name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize display titles in every published conference pack."
    )
    parser.add_argument("public_root", type=Path)
    args = parser.parse_args()

    repository_root = Path(__file__).resolve().parents[3]
    public_root = args.public_root.resolve()
    conference_root = public_root / "v1" / "conferences"
    manifest_path = conference_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    subprocess.run(["cargo", "build", "--quiet"], cwd=repository_root, check=True)
    packer = repository_root / "target" / "debug" / "apaper-cloud"
    changed: list[str] = []
    normalized_total = 0

    with tempfile.TemporaryDirectory(prefix="apaper-title-normalization-") as directory:
        temporary_root = Path(directory)
        for venue in manifest["venues"]:
            for edition in venue["editions"]:
                pack = edition.get("pack")
                if pack is None:
                    continue
                source = conference_root / pack["path"]
                jsonl = temporary_root / f"{venue['id']}-{edition['year']}.jsonl"
                rebuilt = temporary_root / f"{venue['id']}-{edition['year']}.jsonl.zst"
                with jsonl.open("wb") as output:
                    subprocess.run(
                        ["zstd", "--quiet", "--decompress", "--stdout", str(source)],
                        check=True,
                        stdout=output,
                    )
                output = command_output(
                    [str(packer), "pack", "--input", str(jsonl), "--output", str(rebuilt)],
                    repository_root,
                )
                normalized = output_value(output, "normalized_title_count")
                if normalized == 0:
                    continue
                rebuilt.replace(source)
                data = source.read_bytes()
                pack["compressed_bytes"] = len(data)
                pack["sha256"] = hashlib.sha256(data).hexdigest()
                changed.append(f"{venue['id']}:{edition['year']}")
                normalized_total += normalized
                print(f"normalized {venue['id']}:{edition['year']} titles={normalized}")

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"changed_packs={len(changed)}")
    print(f"normalized_titles={normalized_total}")
    for edition_id in changed:
        print(f"changed_pack={edition_id}")


if __name__ == "__main__":
    main()
