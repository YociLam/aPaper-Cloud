# aPaper Translation Engine distribution

This directory defines and validates the architecture-specific aPaper Translation Engine distribution. The engine source remains canonical in the aPaper repository under `third_party/pdfmathtranslate`; it is not duplicated here. The builder packages that fixed local source with a pinned standalone CPython runtime, pinned wheels, layout model, target font, worker protocol, licenses, and integrity manifest.

The runtime never needs system Python, Homebrew, Conda, global `pip`, or an existing virtual environment. Build inputs are immutable by version and verified by SHA-256. GitHub Releases contain only final architecture packages and their release metadata; normal Git history contains only environment definitions, locks, schemas, build/validation scripts, checksums, provenance, and release metadata.

## Current engine artifact: v0.2 (macOS arm64)

[Download the immutable v0.2 Release](https://github.com/YociLam/aPaper-Cloud/releases/tag/translation-engine-v0.2). The [release record](releases/translation-engine-v0.2.json) binds the full archive, complete file inventory, deterministic recipe and exact source revision. Artifact revision **v0.2**, translator **v0.6**, dependency environment ABI **v0.1** and worker protocol **1** are separate identities. This release is macOS Apple Silicon only; no new x86_64 distribution is claimed.

The archive includes layout-aware paragraph continuation, bounded repair and independent-block recovery when continuation delimiters are malformed, formula checks, and paired source/translation block regions. Its source, runtime, models, fonts, license notices and integrity inventory are contained in the full package. The published recipe records the source-overlay hashes and immutable base commitments. Source/recipe change time: **2026-10-21 14:19:11 UTC**; GitHub records publication time separately.

This is an explicit maintainer download and verified App-resource snapshot, not a separate automatic engine updater or a new App release. The status-only component record and website describe v0.6/v0.2 from the inspected signed App bundle. Historical manifests, routes, both v0.1 architecture archives and App update feeds are retained unchanged.

## Historical environment distribution

The archived Cloud metadata records translator `v0.3` and required environment `v0.1`; it does not describe the current App translator. Both use the two-component `vX.Y` product version format, but they are independent: changing only the translator version does not reinstall the environment. The environment supports macOS `arm64` and `x86_64`, minimum macOS 13.0, worker protocol 1. The retained historical metadata endpoint is `https://cloud.apaper.ai/v1/translation/v0.1/manifest.json`; GitHub Release assets are available for explicit manual downloads only.

The source copy inside a complete environment archive is a self-contained bootstrap baseline, not the active translator-version authority. The active translator source is maintained in the aPaper repository and shipped inside the signed App bundle; Cloud does not publish a second translator source package. At runtime aPaper deploys only the matching translator and environment resources carried by that App bundle. A translator-only App update therefore replaces only the translator deployment; the environment remains `v0.1` unless a later App bundle declares another required environment version.

`cloud-route/` is a deliberately narrow Cloudflare Worker. It accepts only GET/HEAD for the two committed package paths and redirects them to immutable Translation Engine Release assets. Unknown paths, query strings, and mutating requests are rejected; it is not a general-purpose GitHub proxy. Its route is limited to the versioned Translation Engine asset prefix and leaves the Pages-hosted control manifest, the conference catalog paths, and the rest of `cloud.apaper.ai` untouched.

Package URLs reserve a platform-first namespace: `/v1/translation/<environment-version>/assets/<platform>/<architecture>/...`. Environment `v0.1` publishes only `macos/arm64` and `macos/x86_64` for explicit manual downloads; the current App does not select or download either package from the network. The sibling `windows/x86_64` and `windows/arm64` namespaces are reserved for future verified Windows distributions, but intentionally have no manifest entries, routes, or placeholder assets today and therefore cannot be selected by a current App. A future Windows release must add its own pinned runtime, dependency lock, compatibility metadata, health check, byte size, and SHA-256 before activating either namespace.

To reproduce a package, download the exact runtime and build inputs recorded under `environment/`, download wheels using `requirements.lock` for CPython 3.12 and the target macOS architecture, and run:

```sh
python3.12 scripts/build-translation-engine-environment.py \
  --engine-source-directory /absolute/path/to/AtomPaper/third_party/pdfmathtranslate \
  --architecture arm64 \
  --translator-version v0.3 \
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

## Retention policy (Update-01-Q2)

The landing page shows App-bundled resource versions/times from the separate status-only
`/v1/app/macos/arm64/components/translation.json`; it no longer polls historical translator metadata. Existing JSON schemas, values,
URLs, Worker configuration and release assets remain unchanged: historical client usage has not
been ruled out. This is presentation deprecation, not endpoint retirement or Worker undeployment.

The local App arm64 `build-assets/translation-engine/package-recipe-v0.1-r1.json` uses
`translation-engine-v0.1/apaper-translation-engine-v0.1-macos-arm64.tar.gz` as its immutable base
(253742792 bytes, SHA-256 `62aa20d956367b0475f3a7af8b67fad99bf7b62a5562e50b90a5ceaa57459ff7`).
Retain the entire `translation-engine-v0.1` Release, including both architectures and inventory
JSON. Do not overwrite or retag assets. The App's translator v0.4 and environment v0.1-r1 are
bundled App resources, not Cloud v0.4 assets. Environment v0.1 and translator v0.4 are independent
versions; r1 identifies a revised environment archive, not a newer environment protocol.
