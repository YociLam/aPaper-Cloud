# aPaper Cloud

`aPaper Cloud` is a static, versioned distribution project for public aPaper
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

ACL 2025 is built from the official ACL Anthology XML collections. The pack
contains the main ACL volumes and the ACL edition of Findings. Its source-native
groups include Long Papers, Short Papers, Findings, Industry Track, System
Demonstrations, Student Research Workshop and Tutorials. Every record retains
its ACL Anthology landing page as provenance.

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
