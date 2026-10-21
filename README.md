<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a></p>
</div>

# aPaper Cloud

aPaper Cloud distributes aPaper application releases, academic literature metadata, and versioned
runtime resources. It provides the public files and integrity metadata used for software updates
and conference catalog synchronization. Application source code and private research workspaces
are maintained separately.

[Website](https://cloud.apaper.ai) · [Releases](https://github.com/YociLam/aPaper-Cloud/releases) · [Contact](mailto:contact@apaper.ai)

## Contents

1. [Application downloads and updates](#application-downloads-and-updates)
2. [Academic literature metadata](#academic-literature-metadata)
3. [Translation Engine](#translation-engine)
4. [Repository layout](#repository-layout)
5. [Integrity and publication](#integrity-and-publication)

## Application downloads and updates

New installer DMGs are distributed through [aPaper Releases](https://github.com/YociLam/aPaper/releases).
This repository retains full update ZIP archives and channel metadata. Both containers must hold
the same sealed App. Historical assets and their download URLs remain available unchanged.

Stable, beta, and qualification channels remain separate. The native macOS updater reads a
channel-specific appcast. Executable updates require a pinned archive URL, build number, minimum
system version, exact size and production EdDSA signature. The accepted check-only client can read
an information-only item without an enclosure and, after consent, open the product website for
manual installation. No production signing key is replaced by a qualification key. It does not infer the App version from this repository's global
“latest release”, which may belong to another product.

**Availability:** App distribution is currently being qualified. No stable App release is published
through this repository. Qualification prereleases are isolated test builds and are not the normal
installation channel.

Current qualification: [0.1.3 (build 9083)](https://github.com/YociLam/aPaper-Cloud/releases/tag/apaper-update-qualification-20261015-9083), published **2026-10-15 10:38:05 UTC**.

See [App distribution contract](APP-DISTRIBUTION.md) for channel paths, publication order, and
verification requirements. Full application archives belong in Releases, not Git history or Pages.

## Academic literature metadata

Conference data is organized by venue and year. Packs contain bibliographic metadata and links to
original sources, including official landing pages, available PDFs, and DOIs. They do not contain
paper PDFs, account credentials, reading history, or private library content.

| Catalog | Version | Updated (UTC) |
| --- | --- | --- |
| Conference manifest | `v0.16` | 2026-10-14 16:12:47 |

The App checks the lightweight [version record](https://cloud.apaper.ai/v1/conferences/version.json),
retrieves a changed [manifest](https://cloud.apaper.ai/v1/conferences/manifest.json), and verifies its
SHA-256 before using it. Edition packs have independent versions, byte counts, and checksums;
missing or outdated packs can be synchronized without reinstalling the App.

### Coverage

| Venue | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: | ---: |
| NeurIPS | — | 3,540 | 4,493 | 5,823 | announced |
| ICML | — | 1,828 | 2,610 | 3,330 | 6,552 |
| ICLR | — | 435 (partial) | 2,261 (partial) | 3,708 (partial) | 5,359 (partial) |
| CVPR | — | 2,352 | 2,710 | 2,871 | 4,068 |
| ACL | — | 2,150 | 1,982 | 3,353 | 4,806 (partial) |
| AAAI | — | 1,578 | 2,331 | 3,028 | 4,149 |
| IJCAI | — | 850 | 1,047 | 1,279 | 972 |
| EMNLP | — | 2,241 | 2,388 | 3,488 | announced |
| ICCV | — | 2,156 | — | 2,701 | — |
| ECCV | 1,645 | — | 2,387 | — | announced |
| AISTATS | — | — | 547 | 583 | 588 |
| COLT | — | — | — | 181 | 196 |
| AAMAS | — | — | — | 479 | 640 (partial) |
| CoRL | — | — | 264 (partial) | 263 | — |
| RSS | — | — | 134 | 163 | 210 |
| OSDI | — | 55 | 53 | 53 | 136 |
| SOSP | — | 9 (partial) | 43 (partial) | 65 (partial) | — |
| IEEE S&P | — | cataloged | 261 | 65 | 254 (partial / no pack) |
| NDSS | — | 94 | 140 | 211 | 265 |
| ACCV | 277 | — | 269 | — | — |
| MIDL | — | — | — | — | 221 |
| MLHC | — | — | — | — | 74 |
| CHIL | — | — | — | — | 40 |
| MLCB | — | — | — | 23 | — |
| L4DC | — | — | — | — | 106 |

Unqualified counts indicate validated metadata packs. **Partial** means coverage
is incomplete; only editions with a valid pack are selectable; **cataloged** means an edition is recorded but its pack is not yet
published; **announced** means final proceedings are pending. The live manifest is authoritative.
The table uses the catalog publication time; per-edition update times are not currently tracked.

Records preserve source provenance. Categories and source groups are retained only when supplied
by the publisher; missing classifications are not inferred. Some ICLR and SOSP records retain the
build-time provenance marker `temporary_reference_supabase_v1`; this does not introduce an App
runtime connection to Supabase.

The DP-NEW catalog contains: 31 sources (25 conferences and six journals), 77 annual selections, 72 packs. Partial editions are selectable only when they have a valid pack; rows marked no pack are unavailable. Discipline definitions and references share the manifest hash. Venue mappings are reviewed by aPaper, not official OECD venue assignments. See the [execution report](docs/dp-new/DP-NEW-report.md) and [mapping](docs/dp-new/discipline-mapping.md).

## Translation Engine

The current App installs and repairs its translation runtime from resources inside its signed
bundle. Translator updates arrive with App releases; the App does not poll historical Cloud
translation manifests or download an environment package from them at runtime.

| App-bundled resource (macOS arm64) | Version | Updated (UTC) |
| --- | --- | --- |
| Translator | `v0.6` | 2026-10-21 14:19:11 |
| Environment package | `v0.2` | 2026-10-21 14:19:11 |

These values describe the verified bundled resource snapshot shown on the website, not a separate
standalone App download or a stable App release announcement. Translator and environment versions are
independent; `v0.2` is the engine artifact revision and retains environment ABI v0.1. The
[resource status record](https://cloud.apaper.ai/v1/app/macos/arm64/components/translation.json)
records their exact package hashes.

[Translation Engine v0.2 (macOS arm64)](https://github.com/YociLam/aPaper-Cloud/releases/tag/translation-engine-v0.2) provides the exact verified full engine archive, file inventory and deterministic recipe for manual download. It includes layout-aware continuation recovery and paired block alignment; x86_64 remains on its historical package. Existing Apps receive translator changes through App updates.

The historical `translation-engine-v0.1` Release and `/v1/translation/` endpoints remain available
for compatibility, explicit maintainer downloads, and reproducible build inputs. In particular,
the original arm64 archive remains the pinned base for the r1 recipe. Historical assets are not
overwritten or relabeled as newer engine packages. See [Translation Engine distribution](translation-engine/README.md).

## Repository layout

```text
public/
  index.html                           Public resource status page
  v1/app/macos/arm64/
    components/translation.json         App-bundled resource status
    <channel>/appcast.xml               App update feed, when published
  v1/conferences/
    version.json                       Catalog version and manifest checksum
    manifest.json                      Venues, editions, and pack integrity metadata
    packs/<venue>/<year>.jsonl.zst      Compressed bibliographic records
  v1/translation/                      Historical compatibility metadata
translation-engine/                    Environment provenance, recipes, and legacy asset route
src/                                  Catalog packaging and validation tools
APP-DISTRIBUTION.md                     App release and channel contract
```

New App ZIPs and historical environment archives are GitHub Release assets here; new installer
DMGs belong in aPaper Releases. Existing Cloud DMGs are retained. The static public
origin is `https://cloud.apaper.ai`; conference manifest paths remain relative to that origin.

## Integrity and publication

Published metadata is validated against its schema, record count, size, and SHA-256. App update
archives additionally require native code-signature checks and a Sparkle EdDSA signature. Stable
automatic installation requires its own trusted signature and native qualification. Apple paid
membership/notarization is deferred for the explicitly labeled ad-hoc manual distribution lane;
that does not disable safe version checks or waive the existing notarized production lane gates.
No public binary or stable channel promotion is announced by this documentation change.

Every App or bundled-resource publication must synchronize the relevant version, build, update
time, and download links in **both READMEs and the website**. Use the actual signed artifacts and
resource-change records; do not use a website deployment time as an engine update time. Upload and
verify immutable Release assets before publishing an appcast that references them. Preserve
unrelated conference packs and historical compatibility endpoints.

Run catalog validation from this repository root:

```sh
cargo run --locked -- validate-site public
cargo test --locked
```

GitHub Actions validates the catalog and Translation Engine distribution before publication.
The legacy asset route has separate tests and a Worker packaging dry-run; updating its development
tooling does not deploy or remove the production Worker.

## E1 journal metadata

Schema 1 keeps conferences in `venues` and adds a separate `journals` extension. Older clients do not enumerate journals; supported clients retain explicit journal kind, ISSNs, native article type, actual volume/issue/article number and original date precision. Annual packs are distribution partitions. The six licensed 2026 snapshots contain 1,552 records through 2026-10-14T15:44:19Z. JLB is usable partial/10 with 14 NC/ND-license exclusions and two unresolved license/abstract records; the other five are complete for their declared input/scope/cutoff, not the future full year. All preceding 66 packs are byte-preserved. The v0.16 release uses the same verified snapshot bytes. See [contract](docs/dp-new/E1-journal-contract.md) and source reconciliation receipts in docs/dp-new/evidence/e1/.
