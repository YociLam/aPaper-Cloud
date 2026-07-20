# Temporary Reference Supabase Channel

Marker: `TEMPORARY_REFERENCE_SUPABASE_CHANNEL`

Channel ID stored in imported records:
`temporary_reference_supabase_v1`

## Purpose

This bridge temporarily reads accepted ICLR and SOSP metadata from the public
Supabase configured by `reference-projects/daily-paper-reader-main`. It exists
only to fill catalog gaps while aPaper's publisher-owned ingestion paths are
being completed.

The bridge is build-time only:

```text
reference Supabase -> temporary importer -> normalized JSONL -> aPaper Cloud pack
```

The macOS app does not receive the Supabase URL or anon key and does not query
Supabase at runtime.

## Deliberate limitations

- ICLR rows have complete accepted-paper metadata and author-provided keywords,
  but the reference table has no PDF URLs.
- SOSP rows contain ACM PDF URLs that currently return browser challenge pages
  to aPaper's downloader.
- The importer therefore preserves only PDF URLs already present in a previous,
  validated aPaper pack. Other records remain searchable and retain their
  publisher landing page, but do not claim a working direct PDF.
- Incomplete rows are skipped and reported; they are not padded with inferred or
  LLM-generated metadata.
- Every generated record carries
  `"metadata_channel":"temporary_reference_supabase_v1"`.

## Removal checklist

1. Replace each marked edition with a pack generated from the official
   publisher-owned importer.
2. Verify that no record in `public/v1/conferences/packs/` contains the channel
   ID.
3. Remove `import_reference_supabase_temporary.py` and this document.
4. Remove the temporary-channel section from `SKILL.md` and `README.md`.
5. Bump the manifest version, regenerate `version.json`, validate, and publish.

Useful audit command:

```sh
for pack in public/v1/conferences/packs/*/*.jsonl.zst; do
  if zstd -dc "$pack" | grep -q 'temporary_reference_supabase_v1'; then
    echo "$pack"
  fi
done
```
