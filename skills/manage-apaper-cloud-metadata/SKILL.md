---
name: manage-apaper-cloud-metadata
description: Maintain and publish aPaper conference metadata packs, edition availability, checksums, and version manifests. Use when adding or refreshing any existing or new conference, validating packs, changing the DailyPaper catalog, publishing to cloud.apaper.ai, or verifying that the App startup version-sync contract can discover a release.
---

# Maintain aPaper Cloud Metadata

Use this skill for changes under `apaper-cloud/public/v1/conferences/`. Locate the repository checkout first and treat its `apaper-cloud` directory as `CLOUD_ROOT`; do not assume a fixed checkout path. The directory is the source of truth for conference editions exposed by DailyPaper; the macOS app synchronizes the catalog from the configured public origin only when the remote manifest version changes and reuses only a previously verified local cache when the network is unavailable.

## App startup synchronization contract

- The App first requests `https://cloud.apaper.ai/v1/conferences/version.json` and compares its two-segment string `manifest_version` with the locally persisted version.
- If the versions are equal, the App must not download the manifest or resynchronize conference packs.
- If the versions differ, the App downloads `manifest.json`, verifies its SHA-256 against `version.json`, updates the catalog, and schedules edition-pack synchronization through the existing bounded background queue.
- Store `manifest_version` as a two-segment numeric string such as `0.9` or `0.10`; never encode it as a JSON number. Advance the minor segment once per metadata release and reserve the major segment for an intentional catalog-protocol milestone. Never reuse a version for changed content, because the App treats exact equality as unchanged.
- Selection-time recovery for a missing or corrupt pack remains a fallback; it does not replace startup synchronization.
- The verified remote Manifest is the complete conference-source catalog. The production App must not bundle a conference catalog fallback: a first launch without a successful Manifest synchronization exposes only arXiv and bioRxiv and leaves the conference list empty.
- Every venue must provide `name` as the canonical English name plus a `localized_names` map containing at least `en` and `zh-Hans`. Add future languages to this map without changing the App catalog code.

## Workflow

1. Resolve the venue workflow:
   - read `skills/extract-<venue>-metadata/SKILL.md` when it exists;
   - for a new venue, create that Skill from verified publisher documentation, keep it venue-specific, and validate it before collecting data;
   - add the venue itself, its cadence, localized names, and editions to the Manifest so the App can expose it without a new binary release;
   - never copy inferred category rules from another venue.
2. Acquire metadata only from the conference or proceedings publisher. Keep the source URL and source-native track/category in every JSONL record.
3. Add or update the compressed pack under `public/v1/conferences/packs/<venue>/<year>.jsonl.zst`. This path convention applies to existing and newly added venues without changing the publishing scripts.
4. Update `manifest.json`:
   - advance the two-segment `manifest_version` once for every catalog or pack release;
   - set `paper_count` and pack `record_count` to the exact same value;
   - use `published` only when metadata and public PDF links have been verified;
   - keep unavailable or unverified editions `cataloged`, `partial`, or `announced` with `pack: null`.
5. Run `python3 skills/manage-apaper-cloud-metadata/scripts/update_version.py public` to rewrite `version.json` with the manifest SHA-256.
6. Update the catalog summaries near the top of both `README.md` (default English) and `README.zh-CN.md` from the final manifest: current version, UTC update time, every listed venue/year count, and non-published state labels must match exactly. Keep the language switch and shared `assets/aPaper.png` header intact. Do not present `cataloged`, `partial`, or `announced` editions as downloadable packs.
7. Validate before publishing:

   ```sh
   cargo run --quiet --manifest-path Cargo.toml -- validate-site public
   cargo test --manifest-path Cargo.toml
   cargo test --manifest-path ../rust/Cargo.toml -p apaper_discovery --lib
   ```

8. Publish `apaper-cloud/public` to the existing production deployment behind `https://cloud.apaper.ai` only after validation succeeds. Never publish a pack with a guessed checksum or a source URL that has not been tested.
9. After deployment, verify the live release and every pack changed by this release. Pass each changed or newly added edition explicitly; venue IDs are resolved from the manifest, so this command also supports future conferences without script changes:

   ```sh
   python3 skills/manage-apaper-cloud-metadata/scripts/verify_published_release.py \
     --public public \
     --origin https://cloud.apaper.ai \
     --pack <venue>:<year> \
     --pack <venue>:<year>
   ```

   Do not report the upload complete unless the live `manifest_version`, manifest SHA-256, and every supplied pack's byte count and SHA-256 match the local release. A CDN, Worker, Pages, DNS, or deployment mismatch is a failed release even when the source repository upload succeeded.

## Contract rules

- Edition IDs are `<venue_id>:<year>` and years are integers.
- `version.json` must match `manifest.json` in schema, dataset, `manifest_version`, and SHA-256.
- `canonical_origin` must remain `https://cloud.apaper.ai`; do not restore a GitHub Pages or raw-repository runtime fallback.
- The app has a bounded selection cap of 20,000 records; do not remove that guard.
- Conference editions are selected by exact venue/year, not by a rolling date window.
- Conference venue availability, ordering, names, translations, cadence, and editions come from the remote Manifest rather than a hard-coded App list.
- Source groups describe the publisher's own track or collection. They are not inferred research topics.
- A venue name, edition label, or broad conference domain is not a paper category. Do not publish values such as `CVPR-2025`, `icml`, or a shared `security` label as per-paper subject evidence.
- Leave ISSN empty when the proceedings series has no verified ISSN. Do not copy an ISSN from a related journal, newsletter, or operating-systems review series.
- Do not commit PDFs to the metadata repository; packs contain metadata and validated public PDF URLs only.

## Source-native category refreshes

- AAAI 2023–2024 expose per-paper subjects as `DC.Subject` metadata. Decompress the existing pack to JSONL, run `scripts/enrich_aaai_subjects.py`, then repack it. AAAI 2025 does not expose the same field; retain its verified OJS technical-track group instead of treating missing subjects as an error in the published pack.
- OSDI technical-session names are an exact official paper grouping. Run `scripts/enrich_osdi_sessions.py --year <year>` against a decompressed OSDI JSONL pack, and require every paper URL to map before repacking.
- If an official proceedings source has no complete per-paper topic, track, or session mapping, leave `source_group` empty. Never infer a display category from the title, abstract, conference name, or an LLM.

## Temporary reference Supabase channel

`scripts/import_reference_supabase_temporary.py` is a removable build-time
bridge for ICLR/SOSP metadata. It must never become an App runtime dependency.
Every imported record is marked with
`metadata_channel=temporary_reference_supabase_v1`; preserve that marker until
the edition is replaced from a publisher-owned source. Read
`TEMPORARY_REFERENCE_SUPABASE_CHANNEL.md` before using or removing the bridge.

Do not copy the reference project's Supabase credentials into this repository.
The importer reads its local `config.yaml` only while generating a pack. It
must not copy OpenReview/ACM challenge URLs into `pdf_url`; preserve only URLs
from an existing pack that have already passed aPaper's PDF validation.

When a temporary ICLR or SOSP pack is missing public PDF URLs, run
`scripts/enrich_open_access_pdfs.py` on the decoded or compressed pack before
publishing it. The script accepts only exact-title OpenAlex matches on aPaper's
trusted HTTPS hosts and verifies the `%PDF-` header. Keep its lookup cache
outside the repository so interrupted runs can resume without committing API
responses.

## Release checklist

- Confirm at least one sample PDF per source/track returns `%PDF-`.
- Confirm every record has title, authors, landing URL, provenance URL, and publication year.
- Confirm `record_count`, `paper_count`, compressed byte size, and SHA-256.
- Run the validator and tests from the repository root.
- Advance `manifest_version` only once per release and regenerate `version.json` after the final manifest edit.
- Confirm both README catalog tables, displayed manifest versions, and UTC update times match the final manifest.
- Deploy, then run `verify_published_release.py` with every changed edition.
- Confirm the live version endpoint differs from the preceding release and exactly matches the new local version and manifest SHA-256.
- When adding a new venue, add and validate its venue-specific extraction Skill, manifest entry, pack directory, official source provenance, localized App presentation where required, and release verification arguments.
