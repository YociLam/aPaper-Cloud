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

The temporary origin is GitHub Pages. The production origin will be
`https://cloud.apaper.ai`. Pack paths in the manifest are relative, so moving
between origins does not change the app protocol or require rebuilding packs.

## Boundary

- The app reads a bounded manifest and selected immutable metadata packs.
- Rust verifies schema version, record count, compressed size and SHA-256.
- Swift never downloads, parses or indexes conference metadata.
- Packs contain metadata only. PDFs remain source-hosted and are opened or
  imported only after an explicit user action.
- Local cached packs live below `~/Documents/aPaper`, never in the checkout.

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
needed by `manifest.json`. Acquisition adapters are intentionally separate from
this normalization and publishing boundary.
