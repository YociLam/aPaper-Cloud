# aPaper Translation Engine distribution

This directory defines and validates the architecture-specific aPaper Translation Engine distribution. The engine source remains canonical in the aPaper repository under `third_party/pdfmathtranslate`; it is not duplicated here. The builder packages that fixed local source with a pinned standalone CPython runtime, pinned wheels, layout model, target font, worker protocol, licenses, and integrity manifest.

The runtime never needs system Python, Homebrew, Conda, global `pip`, or an existing virtual environment. Build inputs are immutable by version and verified by SHA-256. GitHub Releases contain only final architecture packages and their release metadata; normal Git history contains only environment definitions, locks, schemas, build/validation scripts, checksums, provenance, and release metadata.

Translator `v0.1` currently requires environment `v0.1`. Both use the two-component `vX.Y` product version format, but they are independent: changing only the translator version does not reinstall the environment. The environment supports macOS `arm64` and `x86_64`, minimum macOS 13.0, worker protocol 1. The stable public control plane is `https://cloud.apaper.ai/v1/translation/v0.1/manifest.json`; GitHub Release assets are deterministic fallbacks.

The source copy inside a complete environment archive is a self-contained bootstrap baseline, not the active translator-version authority. At runtime aPaper verifies and atomically activates the translator source shipped by the current App under a separate content-addressed translator directory, then runs it with the selected environment's private Python, dependencies, model, and font. A translator-only App update therefore replaces only that translator directory; an environment download occurs only when `required_environment_version`, environment compatibility, integrity, or health requires it.

`cloud-route/` is a deliberately narrow Cloudflare Worker. It accepts only GET/HEAD for the two committed package paths and redirects them to immutable Translation Engine Release assets. Unknown paths, query strings, and mutating requests are rejected; it is not a general-purpose GitHub proxy. Its route is limited to the versioned Translation Engine asset prefix and leaves the Pages-hosted control manifest, the conference catalog paths, and the rest of `cloud.apaper.ai` untouched.

Package URLs reserve a platform-first namespace: `/v1/translation/<environment-version>/assets/<platform>/<architecture>/...`. Environment `v0.1` publishes only `macos/arm64` and `macos/x86_64`; a client selects exactly one matching package and never downloads both. The sibling `windows/x86_64` and `windows/arm64` namespaces are reserved for future verified Windows distributions, but intentionally have no manifest entries, routes, or placeholder assets today and therefore cannot be selected by a current App. A future Windows release must add its own pinned runtime, dependency lock, compatibility metadata, health check, byte size, and SHA-256 before activating either namespace.

To reproduce a package, download the exact runtime and build inputs recorded under `environment/`, download wheels using `requirements.lock` for CPython 3.12 and the target macOS architecture, and run:

```sh
python3.12 scripts/build-translation-engine-environment.py \
  --engine-source-directory /absolute/path/to/AtomPaper/third_party/pdfmathtranslate \
  --architecture arm64 \
  --translator-version v0.1 \
  --environment-version v0.1 \
  --python-archive /absolute/path/to/python.tar.gz \
  --python-sha256 <sha256> \
  --wheelhouse /absolute/path/to/wheels \
  --dependency-lock "$PWD/environment/requirements.lock" \
  --layout-model /absolute/path/to/doclayout.onnx \
  --layout-model-sha256 fece9af02f618b603ff7921ccec6861d13e7e1f9830e091dfb7e8ad9311e5b21 \
  --font /absolute/path/to/SourceHanSerifCN-Regular.ttf \
  --font-sha256 8ba5ec09db04b1d1599edeff3fb5627ca11eaaf85e339e5c32684cb94e806993 \
  --upstream-commit 44c4d5b332705797c1df17fadde2022e7c49f5de \
  --upstream-commitment 9b28216ce7c74ee70d576cc4d1c1a69ba5bde789abf48a0b0f9c98d815d7ec99 \
  --output-directory /absolute/path/to/output
```

The package builder normalizes timestamps, owners, ordering, and gzip metadata. It writes a complete file inventory and SHA-256 commitments into the release metadata. Packaging and publication are separate: a verified local build is uploaded as an immutable GitHub Release, and no intermediate model/font/source asset release is created.

The installed App no longer resolves Translation Engine packages from `cloud.apaper.ai`, GitHub, or
another mirror. It carries the matching translator and environment packages in its signed bundle,
performs a lightweight startup check, and deploys only from those bundled resources. The URLs and
release assets described above remain available for explicit manual downloads and for maintainers
preparing the next App build; they are not an automatic runtime fallback. Conference catalog
synchronization remains a separate App capability. Any manual package transfer still uses the
shared aPaper segmented downloader (maximum 12 workers), and every package is admitted by expected
byte count plus SHA-256 before staged atomic activation.
