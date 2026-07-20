# aPaper Cloud

`apaper-cloud` is a static, versioned distribution project for public aPaper
metadata. It does not store user profiles, reading history, recommendations,
credentials, PDFs, or other private workspace data.

The first published dataset is the DailyPaper conference catalog. Conference
metadata is split by exact venue edition so the app downloads only the years a
user selects:

```text
public/
  v1/
    conferences/
      manifest.json
      packs/<venue>/<year>.jsonl.zst
```

The temporary origin is `https://yocilam.github.io/aPaper-Cloud`. The
production origin will be `https://cloud.apaper.ai`. Pack paths in the manifest
are relative, so moving between origins does not change the app protocol or
require rebuilding packs.

Some ICLR/SOSP catalog gaps are temporarily filled at build time from the
public Supabase configured by the bundled `daily-paper-reader-main` reference
project. This is not an App runtime dependency. Such records carry
`metadata_channel=temporary_reference_supabase_v1`; the importer, limitations,
and removal checklist live in
`skills/manage-apaper-cloud-metadata/TEMPORARY_REFERENCE_SUPABASE_CHANNEL.md`.
The App temporarily pins the distribution commit through jsDelivr to avoid a
stale `@main` cache; this pin is removed when `cloud.apaper.ai` becomes the
production origin.

## Boundary

- The app reads a bounded manifest and selected immutable metadata packs.
- Rust verifies schema version, record count, compressed size and SHA-256.
- Swift never downloads, parses or indexes conference metadata.
- Packs contain metadata only. PDFs remain source-hosted and are opened or
  imported only after an explicit user action.
- Local cached packs live below `~/Documents/aPaper`, never in the checkout.
- `source_group` preserves the source's own proceedings track or volume. It is
  not an inferred research topic and is displayed separately from query-group
  evidence in DailyPaper.

## Published sources

Only editions whose public metadata and paper PDFs were verified are marked
`published` in the manifest. The current catalog includes official metadata for
ACL, EMNLP, ICML, NeurIPS, AAAI, CVPR, ECCV, IJCAI, OSDI, IEEE S&P and NDSS.
Each record retains the official landing page and PDF URL as provenance.

ICLR 2023 and SOSP 2023 remain independently verified arXiv-backed subsets.
ICLR 2024–2026 and SOSP 2024–2025 are `partial` editions assembled through the
temporary reference Supabase channel: accepted-paper metadata is searchable,
while only direct PDF URLs inherited from an already validated aPaper pack are
retained. Records whose only PDF endpoint is an OpenReview or ACM
browser-challenge page keep their publisher landing page but do not claim a
working direct PDF.

Source-native groups are preserved when the proceedings expose them: ACL and
EMNLP volumes, AAAI technical tracks, NeurIPS tracks and IJCAI subject areas are
examples. These labels are publication metadata, not inferred research topics.
Editions that cannot yet provide a stable public PDF boundary remain cataloged
but unavailable for selection.

## Tooling

Validate the checked-in static site:

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- validate-site apaper-cloud/public
```

Build one immutable pack from normalized JSON Lines:

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- pack \
  --input /path/to/acl-2025.jsonl \
  --output apaper-cloud/public/v1/conferences/packs/acl/2025.jsonl.zst
```

The pack command prints the record count, compressed byte count and SHA-256
needed by `manifest.json`.

Build the ACL pack directly from official ACL Anthology XML:

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- ingest-acl \
  --input /path/to/2025.acl.xml \
  --input /path/to/2025.findings.xml \
  --venue acl \
  --edition acl:2025 \
  --year 2025 \
  --output /tmp/acl-2025.jsonl
```

Acquisition adapters remain separate from the app-facing normalization and
publishing boundary.
