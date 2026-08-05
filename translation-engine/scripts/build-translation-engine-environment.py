#!/usr/bin/env python3
"""Build deterministic, architecture-specific aPaper Translation Engine archives."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tarfile
import tempfile
from typing import Iterable
import zipfile


SCHEMA_VERSION = 1
WORKER_PROTOCOL_VERSION = 1
RUNTIME_PDF2ZH_FILES = (
    "__init__.py",
    "apaper_gateway.py",
    "converter.py",
    "converter_docx.py",
    "doclayout.py",
    "high_level.py",
    "pdfinterp.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sha256(path: Path, expected: str) -> None:
    if len(expected) != 64 or sha256(path) != expected:
        raise RuntimeError(f"integrity mismatch: {path.name}")


def safe_archive_path(name: str) -> PurePosixPath:
    value = PurePosixPath(name)
    if value.is_absolute() or not value.parts or any(part in {"", ".", ".."} for part in value.parts):
        raise RuntimeError(f"unsafe archive member: {name}")
    return value


def extract_runtime(archive: Path, destination: Path) -> None:
    extract_root = destination / ".runtime-extract"
    extract_root.mkdir()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            relative = safe_archive_path(member.name)
            if member.issym() or member.islnk():
                target = PurePosixPath(member.linkname)
                if target.is_absolute() or any(part == ".." for part in target.parts):
                    raise RuntimeError(f"unsafe runtime link: {member.name}")
            output = extract_root.joinpath(*relative.parts)
            if member.isdir():
                output.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                output.parent.mkdir(parents=True, exist_ok=True)
                source = bundle.extractfile(member)
                if source is None:
                    raise RuntimeError(f"runtime member unavailable: {member.name}")
                with output.open("wb") as handle:
                    shutil.copyfileobj(source, handle)
                output.chmod(member.mode & 0o777)
            elif member.issym():
                output.parent.mkdir(parents=True, exist_ok=True)
                output.symlink_to(member.linkname)
            elif member.islnk():
                link_source = extract_root.joinpath(*safe_archive_path(member.linkname).parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                os.link(link_source, output)
            else:
                raise RuntimeError(f"unsupported runtime member: {member.name}")
    install = extract_root / "python"
    if not (install / "bin" / "python3").is_file():
        raise RuntimeError("standalone Python layout is invalid")
    shutil.move(str(install), str(destination / "python"))
    shutil.rmtree(extract_root)
    materialize_symlinks(destination / "python")


def materialize_symlinks(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda value: value.as_posix()):
        if not path.is_symlink():
            continue
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
            raise RuntimeError(f"unsafe runtime symlink: {path}")
        path.unlink()
        shutil.copy2(resolved, path)


def wheel_destination(name: PurePosixPath, site_packages: Path, scripts: Path) -> Path | None:
    parts = list(name.parts)
    data_index = next((index for index, part in enumerate(parts) if part.endswith(".data")), None)
    if data_index is None:
        return site_packages.joinpath(*parts)
    if len(parts) <= data_index + 2:
        return None
    category = parts[data_index + 1]
    remainder = parts[data_index + 2 :]
    if category in {"purelib", "platlib"}:
        return site_packages.joinpath(*remainder)
    if category == "scripts":
        return scripts.joinpath(*remainder)
    return None


def install_wheels(wheelhouse: Path, python_root: Path) -> list[str]:
    site_packages = python_root / "lib" / "python3.12" / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)
    scripts = python_root / "bin"
    wheels = sorted(wheelhouse.glob("*.whl"), key=lambda path: path.name.lower())
    if not wheels:
        raise RuntimeError("wheelhouse is empty")
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as bundle:
            for info in sorted(bundle.infolist(), key=lambda value: value.filename):
                if info.is_dir():
                    continue
                relative = safe_archive_path(info.filename)
                output = wheel_destination(relative, site_packages, scripts)
                if output is None:
                    continue
                output.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(info) as source, output.open("wb") as handle:
                    shutil.copyfileobj(source, handle)
                mode = (info.external_attr >> 16) & 0o777
                if mode:
                    output.chmod(mode)
    return [wheel.name for wheel in wheels]


def copy_engine_source(integration: Path, root: Path, model: Path, font: Path) -> None:
    runtime_library = root / "engine" / "lib" / "pdf2zh"
    runtime_library.mkdir(parents=True)
    for directory in [root / "engine" / "worker", root / "models", root / "fonts", root / "licenses"]:
        directory.mkdir(parents=True, exist_ok=True)
    for name in RUNTIME_PDF2ZH_FILES:
        shutil.copy2(integration / "upstream" / "pdf2zh" / name, runtime_library / name)
    shutil.copy2(
        integration / "engine" / "apaper_translation_worker.py",
        root / "engine" / "worker" / "apaper_translation_worker.py",
    )
    shutil.copy2(
        integration / "engine" / "worker-protocol.schema.json",
        root / "engine" / "worker" / "worker-protocol.schema.json",
    )
    shutil.copy2(model, root / "models" / "doclayout.onnx")
    shutil.copy2(font, root / "fonts" / "SourceHanSerifCN-Regular.ttf")
    shutil.copy2(integration / "upstream" / "LICENSE", root / "licenses" / "PDFMathTranslate-AGPL-3.0.txt")
    shutil.copy2(integration / "UPSTREAM.md", root / "licenses" / "PDFMathTranslate-UPSTREAM.md")
    shutil.copy2(integration / "APAPER_MODIFICATIONS.md", root / "licenses" / "PDFMathTranslate-APAPER-MODIFICATIONS.md")


def file_inventory(root: Path, excluded: set[str] | None = None) -> list[dict[str, object]]:
    excluded = excluded or set()
    entries: list[dict[str, object]] = []
    for path in sorted(
        (path for path in root.rglob("*") if path.is_file() and not path.is_symlink()),
        key=lambda value: value.as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})
    return entries


def dependency_notices(root: Path) -> list[dict[str, str]]:
    notices: list[dict[str, str]] = []
    site_packages = root / "python" / "lib" / "python3.12" / "site-packages"
    for metadata in sorted(site_packages.glob("*.dist-info/METADATA")):
        fields: dict[str, str] = {}
        for line in metadata.read_text("utf-8", errors="replace").splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            if key in {"Name", "Version", "License"} and key not in fields:
                fields[key] = value.strip()
        notices.append(
            {
                "name": fields.get("Name", metadata.parent.name),
                "version": fields.get("Version", "unknown"),
                "license": fields.get("License", "see package metadata"),
            }
        )
    return notices


def add_tar_path(bundle: tarfile.TarFile, path: Path, arcname: str) -> None:
    info = bundle.gettarinfo(str(path), arcname=arcname)
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "wheel"
    info.mtime = 0
    if info.isfile():
        with path.open("rb") as handle:
            bundle.addfile(info, handle)
    else:
        bundle.addfile(info)


def deterministic_tar_gz(
    root: Path,
    output: Path,
    prefixes: Iterable[str] | None = None,
    excluded_prefixes: Iterable[str] | None = None,
) -> None:
    selected = tuple(prefixes or ("",))
    excluded = tuple(excluded_prefixes or ())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as bundle:
                paths = sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix())
                for path in paths:
                    relative = path.relative_to(root).as_posix()
                    if not any(relative == prefix.rstrip("/") or relative.startswith(prefix) for prefix in selected):
                        continue
                    if any(relative == prefix.rstrip("/") or relative.startswith(prefix) for prefix in excluded):
                        continue
                    add_tar_path(bundle, path, relative)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-source-directory", type=Path, required=True)
    parser.add_argument("--architecture", choices=["arm64", "x86_64"], required=True)
    parser.add_argument("--minimum-macos", default="13.0")
    parser.add_argument("--engine-version", required=True)
    parser.add_argument("--python-archive", type=Path, required=True)
    parser.add_argument("--python-sha256", required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--dependency-lock", type=Path, required=True)
    parser.add_argument("--layout-model", type=Path, required=True)
    parser.add_argument("--layout-model-sha256", required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--font-sha256", required=True)
    parser.add_argument("--upstream-commitment", required=True)
    parser.add_argument("--upstream-commit", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    arguments = parser.parse_args()

    for path in [arguments.engine_source_directory, arguments.wheelhouse]:
        if not path.is_absolute() or not path.is_dir():
            raise RuntimeError(f"directory input is invalid: {path}")
    for path in [arguments.python_archive, arguments.dependency_lock, arguments.layout_model, arguments.font]:
        if not path.is_absolute() or not path.is_file():
            raise RuntimeError(f"file input is invalid: {path}")
    validate_sha256(arguments.python_archive, arguments.python_sha256)
    validate_sha256(arguments.layout_model, arguments.layout_model_sha256)
    validate_sha256(arguments.font, arguments.font_sha256)
    dependency_lock_commitment = sha256(arguments.dependency_lock)

    with tempfile.TemporaryDirectory(prefix="apaper-translation-environment-") as temporary:
        root = Path(temporary) / "engine-root"
        root.mkdir()
        extract_runtime(arguments.python_archive, root)
        wheels = install_wheels(arguments.wheelhouse, root / "python")
        copy_engine_source(
            arguments.engine_source_directory,
            root,
            arguments.layout_model,
            arguments.font,
        )
        notices = dependency_notices(root)
        (root / "licenses" / "python-packages.json").write_text(
            json.dumps(notices, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "utf-8",
        )
        inventory = file_inventory(root, {"engine-manifest.json"})
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "engine_version": arguments.engine_version,
            "backend": "python_pdfmathtranslate",
            "architecture": arguments.architecture,
            "minimum_macos_version": arguments.minimum_macos,
            "worker_protocol_version": WORKER_PROTOCOL_VERSION,
            "python_version": "3.12.13",
            "python_build_release": "20260602",
            "pdfmathtranslate_version": "1.9.11",
            "pdfmathtranslate_upstream_commit": arguments.upstream_commit,
            "pdfmathtranslate_commitment": arguments.upstream_commitment,
            "dependency_lock_commitment": dependency_lock_commitment,
            "layout_model_sha256": arguments.layout_model_sha256,
            "target_font_sha256": arguments.font_sha256,
            "installed_size": sum(int(entry["bytes"]) for entry in inventory),
            "wheels": wheels,
            "files": inventory,
        }
        (root / "engine-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "utf-8",
        )

        stem = f"apaper-translation-engine-{arguments.engine_version}-macos-{arguments.architecture}"
        full = arguments.output_directory / f"{stem}.tar.gz"
        deterministic_tar_gz(root, full)

        release = dict(manifest)
        release["assets"] = [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in [full]
        ]
        release_path = arguments.output_directory / f"{stem}.release.json"
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2, sort_keys=True) + "\n", "utf-8")
        print(json.dumps(release, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
