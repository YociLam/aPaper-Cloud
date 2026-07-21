<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a></p>
</div>

# aPaper Cloud

`aPaper Cloud` is a static, versioned distribution repository for public aPaper metadata. It does
not store user profiles, reading history, recommendations, account credentials, PDF files, or any
other private workspace data.

The first published dataset is a catalog of academic conference proceedings. Conference metadata
is partitioned by venue and edition year, allowing the App to download only the exact editions it
needs.

- Production origin: `https://cloud.apaper.ai`
- Current manifest: `v0.10`
- Catalog updated: `2026-07-21 18:02:36 UTC`

## Catalog overview

The table below is generated from `public/v1/conferences/manifest.json`. A number without a status
suffix means that the edition pack has been fully published, has passed release validation, and is
available for App synchronization.

| Venue | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ICLR | — | 435 (partial) | 2,261 (partial) | 3,708 (partial) | 5,359 (partial) |
| ICML | — | 1,828 | 2,610 | 3,330 | 6,341 (cataloged) |
| NeurIPS | — | 3,540 | 4,493 | 5,823 | announced |
| AAAI | — | 1,578 | 2,331 | 3,028 | 4,149 |
| CVPR | — | 2,352 | 2,710 | 2,871 | 4,068 |
| ECCV | 1,645 | — | 2,387 | — | announced |
| IJCAI | — | 850 | 1,047 | 1,279 | announced |
| ACL | — | 2,150 | 1,982 | 3,353 | 4,806 |
| EMNLP | — | 2,241 | 2,388 | 3,488 | announced |
| OSDI | — | 55 | 53 | 53 | 136 |
| SOSP | — | 9 (partial) | 43 (partial) | 65 (partial) | — |
| IEEE S&P | — | cataloged | 261 | 65 | 254 (partial) |
| NDSS | — | 94 | 140 | 211 | 265 |
| AISTATS | — | — | 547 | 583 | — |
| COLT | — | — | — | 181 | 196 |
| CoRL | — | — | 264 (partial) | 263 | — |
| RSS | — | — | 134 | 163 | — |
| ICCV | — | 2,156 | — | 949 | — |
| ACCV | 277 | — | 269 | — | — |
| AAMAS | — | — | — | 479 | 639 (partial) |

Status definitions:

- **Published**: the pack has passed record-count, compressed-size, and SHA-256 validation and is
  available for App synchronization.
- **Partial**: a searchable pack exists, but metadata completeness or public PDF coverage remains
  incomplete.
- **Cataloged**: the edition or paper count has been confirmed, but no downloadable pack has been
  published.
- **Announced**: the edition is listed in the catalog, but the final proceedings are not yet ready
  for publication.

The catalog table uses the release-wide manifest timestamp. Per-edition update timestamps are not
currently maintained.

## Repository layout

```text
public/
  v1/
    conferences/
      version.json
      manifest.json
      packs/<venue>/<year>.jsonl.zst
```

- `version.json` is the lightweight endpoint checked first when the App starts.
- `manifest.json` records the complete venue catalog, localized venue names, editions,
  publication states, paper counts, pack sizes, and SHA-256 checksums.
- `packs/<venue>/<year>.jsonl.zst` contains read-only metadata for one exact conference edition.
- Packs contain metadata and validated source links only. They do not contain PDF files.

The canonical production origin is always `https://cloud.apaper.ai`. Pack paths in the manifest are
relative. Adding a venue, changing its localized name, or publishing a new edition therefore does
not require rebuilding the App.

## App synchronization contract

1. On startup, the App requests `version.json` and compares the remote two-segment
   `manifest_version` with its locally persisted version.
2. If the versions match, synchronization stops without downloading the manifest or conference
   packs again.
3. If the versions differ, the App downloads `manifest.json` and verifies it using the SHA-256 in
   `version.json`.
4. The source selector is rebuilt from the verified Manifest, including its localized venue names.
   A first launch with no successful Manifest synchronization shows no conference sources; arXiv
   and bioRxiv remain available independently.
5. After validation, a bounded background queue synchronizes edition packs one at a time to avoid
   concentrated server requests.
6. If a user selects an edition whose local pack is missing or corrupt, the App performs an
   on-demand recovery download.

## Data boundaries

- Rust validates the schema, record count, compressed size, and SHA-256 checksum.
- Swift does not download, parse, or index conference metadata.
- App-owned local caches live under `~/Documents/aPaper`; they are never written into the source
  repository.
- PDFs remain on publisher or conference websites and are accessed only when the user opens or
  imports a paper.
- `source_group` may contain only a publisher-provided track, session, subject, or collection. It
  must not be inferred from a title, abstract, venue name, or language model.
- When no reliable per-paper classification exists, `categories` and `source_group` remain empty.

## Data sources

Published or cataloged venues currently include ICLR, ICML, NeurIPS, AAAI, CVPR, ECCV, IJCAI,
ACL, EMNLP, OSDI, SOSP, IEEE S&P, NDSS, AISTATS, COLT, CoRL, RSS, ICCV, ACCV, and AAMAS. Each
record preserves its official landing URL, PDF URL, DOI when available, and provenance URL.

ICLR 2024–2026 and SOSP 2024–2025 currently include metadata imported through the reference
project's temporary Supabase build-time channel. These records carry
`metadata_channel=temporary_reference_supabase_v1`; the App never connects to Supabase at runtime.
The migration boundary and removal checklist are documented in
`skills/manage-apaper-cloud-metadata/TEMPORARY_REFERENCE_SUPABASE_CHANNEL.md`.

## Maintenance workflow

Each conference has a dedicated extraction Skill under `skills/`. Packaging, release versioning,
validation, and publication are governed by
`skills/manage-apaper-cloud-metadata/SKILL.md`.

A standard update consists of:

1. Read `skills/extract-<venue>-metadata/SKILL.md` and extract records from the verified official
   source.
2. Normalize records to the aPaper conference schema and verify counts, required fields, duplicate
   IDs, and source-native groups.
3. Build the corresponding `.jsonl.zst` edition pack.
4. Update the manifest and advance the two-segment release version once, for example `0.9` →
   `0.10`.
5. Regenerate `version.json`, then run local validation and Rust tests.
6. Publish to GitHub and Cloudflare, and verify the byte size and SHA-256 of every changed pack.

## General-purpose tools

Normalize a publisher-exported JSON array with the shared importer:

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- import-json \
  --input /tmp/<venue>-<year>.json \
  --venue <venue> \
  --edition <venue>:<year> \
  --year <year> \
  --output /tmp/<venue>-<year>.jsonl
```

Package normalized JSONL for publication:

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- pack \
  --input /tmp/<venue>-<year>.jsonl \
  --output apaper-cloud/public/v1/conferences/packs/<venue>/<year>.jsonl.zst
```

Regenerate the lightweight version endpoint after the final manifest edit:

```bash
python3 apaper-cloud/skills/manage-apaper-cloud-metadata/scripts/update_version.py \
  apaper-cloud/public
```

Run the complete local release validation:

```bash
cargo run --quiet --manifest-path apaper-cloud/Cargo.toml -- \
  validate-site apaper-cloud/public
cargo test --manifest-path apaper-cloud/Cargo.toml
cargo test --manifest-path rust/Cargo.toml -p apaper_discovery --lib
```

Verify the release control plane and every changed edition after deployment:

```bash
python3 apaper-cloud/skills/manage-apaper-cloud-metadata/scripts/verify_published_release.py \
  --public apaper-cloud/public \
  --origin https://cloud.apaper.ai \
  --pack <venue>:<year> \
  --pack <venue>:<year>
```

Sources such as ACL Anthology XML, AAAI OAI-PMH, and CVF Open Access use venue-specific extractors.
They are acquisition adapters within each conference Skill, not the project's only import path.
