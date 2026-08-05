#!/usr/bin/env python3
"""Generate the immutable aPaper Translation Engine YAML definition."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import time
from typing import Any
from urllib.request import Request, urlopen
import zipfile


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def asset(path: Path, sources: list[dict[str, str]]) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"asset unavailable: {path}")
    return {
        "name": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "sources": sources,
    }


def wheel_identity(path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(path) as bundle:
        metadata_names = [
            name for name in bundle.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise RuntimeError(f"wheel metadata invalid: {path.name}")
        fields: dict[str, str] = {}
        for line in bundle.read(metadata_names[0]).decode("utf-8", "replace").splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                if key in {"Name", "Version"} and key not in fields:
                    fields[key] = value.strip()
        if set(fields) != {"Name", "Version"}:
            raise RuntimeError(f"wheel identity unavailable: {path.name}")
        return fields["Name"], fields["Version"]


@lru_cache(maxsize=None)
def pypi_release(name: str, version: str) -> dict[str, Any]:
    request = Request(
        f"https://pypi.org/pypi/{name}/{version}/json",
        headers={"User-Agent": "aPaper-Cloud environment-definition-builder/1"},
    )
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except Exception as error:
            last_error = error
            time.sleep(attempt + 1)
    raise RuntimeError(f"PyPI metadata unavailable: {name}=={version}") from last_error


def wheel_assets(wheelhouse: Path) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for wheel in sorted(wheelhouse.glob("*.whl"), key=lambda value: value.name.lower()):
        name, version = wheel_identity(wheel)
        release = pypi_release(name, version)
        candidates = [entry for entry in release.get("urls", []) if entry.get("filename") == wheel.name]
        if len(candidates) != 1:
            raise RuntimeError(f"PyPI wheel source unavailable: {wheel.name}")
        candidate = candidates[0]
        commitment = sha256(wheel)
        if (
            candidate.get("digests", {}).get("sha256") != commitment
            or candidate.get("size") != wheel.stat().st_size
            or not str(candidate.get("url", "")).startswith("https://files.pythonhosted.org/")
        ):
            raise RuntimeError(f"PyPI wheel commitment mismatch: {wheel.name}")
        output.append(
            asset(
                wheel,
                [{"kind": "official", "url": candidate["url"]}],
            )
        )
    if not output:
        raise RuntimeError("wheelhouse is empty")
    return output


def scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise TypeError(f"unsupported YAML scalar: {type(value).__name__}")


def emit_yaml(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(emit_yaml(child, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {scalar(child)}")
        return lines
    if isinstance(value, list):
        lines = []
        for child in value:
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(emit_yaml(child, indent + 2))
            else:
                lines.append(f"{prefix}- {scalar(child)}")
        return lines if lines else [f"{prefix}[]"]
    return [f"{prefix}{scalar(value)}"]


def package_asset(path: Path, version: str, architecture: str, release_tag: str) -> dict[str, Any]:
    name = path.name
    return asset(
        path,
        [
            {
                "kind": "cloud_primary",
                "url": f"https://cloud.apaper.ai/v1/translation/{version}/assets/macos/{architecture}/{name}",
            },
            {
                "kind": "github_release",
                "url": f"https://github.com/YociLam/aPaper-Cloud/releases/download/{release_tag}/{name}",
            },
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-version", required=True)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--package-arm64", type=Path, required=True)
    parser.add_argument("--package-x86-64", type=Path, required=True)
    parser.add_argument("--wheelhouse-arm64", type=Path, required=True)
    parser.add_argument("--wheelhouse-x86-64", type=Path, required=True)
    parser.add_argument("--python-runtimes", type=Path, required=True)
    parser.add_argument("--dependency-lock", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--layout-model", type=Path, required=True)
    parser.add_argument("--layout-model-revision", required=True)
    parser.add_argument("--target-font", type=Path, required=True)
    parser.add_argument("--target-font-revision", required=True)
    parser.add_argument("--pdfmathtranslate-commitment", required=True)
    parser.add_argument("--pdfmathtranslate-upstream-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    runtimes = json.loads(arguments.python_runtimes.read_text("utf-8"))
    source_archive = asset(arguments.source_archive, [])
    model = asset(
        arguments.layout_model,
        [
            {
                "kind": "trusted_third_party",
                "url": "https://huggingface.co/wybxc/DocLayout-YOLO-DocStructBench-onnx/resolve/"
                f"{arguments.layout_model_revision}/{arguments.layout_model.name}",
            }
        ],
    )
    font = asset(
        arguments.target_font,
        [
            {
                "kind": "trusted_third_party",
                "url": "https://raw.githubusercontent.com/timelic/source-han-serif/"
                f"{arguments.target_font_revision}/{arguments.target_font.name}",
            }
        ],
    )
    packages = {
        "arm64": arguments.package_arm64,
        "x86_64": arguments.package_x86_64,
    }
    wheelhouses = {
        "arm64": arguments.wheelhouse_arm64,
        "x86_64": arguments.wheelhouse_x86_64,
    }
    architectures: dict[str, Any] = {}
    for architecture in ["arm64", "x86_64"]:
        runtime = runtimes["architectures"][architecture]
        runtime_name = Path(runtime["url"].replace("%2B", "+")).name
        architectures[architecture] = {
            "package": package_asset(
                packages[architecture],
                arguments.engine_version,
                architecture,
                arguments.release_tag,
            ),
            "fallback": {
                "python_runtime": {
                    "name": runtime_name,
                    "bytes": runtime["bytes"],
                    "sha256": runtime["sha256"],
                    "sources": [{"kind": "official", "url": runtime["url"]}],
                },
                "wheels": wheel_assets(wheelhouses[architecture]),
                "native_dependencies": [],
                "layout_model": model,
                "target_font": font,
                "bundled_source_archive_bytes": source_archive["bytes"],
                "bundled_source_archive_sha256": source_archive["sha256"],
            },
        }

    definition = {
        "schema_version": 1,
        "engine_version": arguments.engine_version,
        "backend_id": "python_pdfmathtranslate",
        "worker_protocol_version": 1,
        "minimum_macos_version": "13.0",
        "python_version": "3.12.13",
        "pdfmathtranslate_version": "1.9.11",
        "pdfmathtranslate_upstream_commit": arguments.pdfmathtranslate_upstream_commit,
        "pdfmathtranslate_commitment": arguments.pdfmathtranslate_commitment,
        "dependency_lock_commitment": sha256(arguments.dependency_lock),
        "install_layout": {
            "python_root": "python",
            "engine_root": "engine",
            "models_root": "models",
            "fonts_root": "fonts",
            "mutable_cache_root": "cache",
        },
        "health_check": {
            "executable": "python/bin/python3",
            "worker": "engine/worker/apaper_translation_worker.py",
            "arguments": ["--health-check"],
            "timeout_seconds": 30,
            "offline_required": True,
        },
        "compatibility": {
            "allowed_worker_protocol_versions": [1],
            "require_exact_engine_version": True,
        },
        "architectures": architectures,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text("\n".join(emit_yaml(definition)) + "\n", "utf-8")
    print(json.dumps({"bytes": arguments.output.stat().st_size, "sha256": sha256(arguments.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
