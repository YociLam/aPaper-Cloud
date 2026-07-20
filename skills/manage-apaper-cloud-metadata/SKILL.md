---
name: manage-apaper-cloud-metadata
description: Maintain aPaper conference metadata packs, edition availability, checksums, and version manifests. Use when adding or refreshing conference years, validating packs, changing the public metadata catalog, or publishing updates for DailyPaper.
---

# Maintain aPaper Cloud Metadata

Use this skill for changes under `apaper-cloud/public/v1/conferences/`. The directory is the source of truth for conference editions exposed by DailyPaper; the macOS app embeds the catalog as a fallback and synchronizes it from the configured public origin when the manifest version changes.

## Workflow

1. Acquire metadata only from the conference or proceedings publisher. Keep the source URL and source-native track/category in every JSONL record.
2. Add or update the compressed pack under `public/v1/conferences/packs/<venue>/<year>.jsonl.zst`.
3. Update `manifest.json`:
   - increment `manifest_version` for every catalog or pack change;
   - set `paper_count` and pack `record_count` to the exact same value;
   - use `published` only when metadata and public PDF links have been verified;
   - keep unavailable or unverified editions `cataloged`, `partial`, or `announced` with `pack: null`.
4. Run `python3 skills/manage-apaper-cloud-metadata/scripts/update_version.py public` to rewrite `version.json` with the manifest SHA-256.
5. Validate before publishing:

   ```sh
   cargo run --quiet --manifest-path Cargo.toml -- validate-site public
   cargo test --manifest-path Cargo.toml
   cargo test --manifest-path ../rust/Cargo.toml -p apaper_discovery --lib
   ```

6. Publish `apaper-cloud` to the configured GitHub Pages repository only after validation succeeds. Never publish a pack with a guessed checksum or a source URL that has not been tested.

## Contract rules

- Edition IDs are `<venue_id>:<year>` and years are integers.
- `version.json` must match `manifest.json` in schema, dataset, `manifest_version`, and SHA-256.
- The app has a bounded selection cap of 20,000 records; do not remove that guard.
- Conference editions are selected by exact venue/year, not by a rolling date window.
- Source groups describe the publisher's own track or collection. They are not inferred research topics.
- Leave ISSN empty when the proceedings series has no verified ISSN. Do not copy an ISSN from a related journal, newsletter, or operating-systems review series.
- Do not commit PDFs to the metadata repository; packs contain metadata and validated public PDF URLs only.

## Release checklist

- Confirm at least one sample PDF per source/track returns `%PDF-`.
- Confirm every record has title, authors, landing URL, provenance URL, and publication year.
- Confirm `record_count`, `paper_count`, compressed byte size, and SHA-256.
- Run the validator and tests from the repository root.
- Increment `manifest_version` only once per release and regenerate `version.json` after the final manifest edit.
