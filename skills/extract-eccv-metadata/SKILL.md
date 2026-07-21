---
name: extract-eccv-metadata
description: Extract, normalize, verify, and publish one ECCV year to aPaper Cloud. Use when ECVA publishes a new ECCV proceedings year or an existing ECCV metadata pack needs repair.
---

# Extract ECCV Metadata

## Source contract

- Use the official ECVA proceedings pages as the authoritative paper source. Preserve each paper landing page and the ECVA PDF URL derived from that page.
- ECVA does not publish a complete per-paper topic taxonomy; leave `source_group` empty unless the official proceedings add one.
- Leave `categories` empty because ECVA does not publish a complete, reliable per-paper topic taxonomy.
- Prefer electronic LNCS ISSN `1611-3349` for library metadata when the proceedings series field applies.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Enumerate all official ECVA paper pages for the requested year, including all parts/volumes, with bounded concurrency and a resume cache.
3. Parse official title, authors, abstract, landing URL, PDF URL, DOI when present, and publication date; normalize to `venue_id=eccv` and `edition_id=eccv:<year>` with empty categories unless ECVA adds an official taxonomy.
4. Validate the ECVA HTML-to-PDF mapping and a deterministic PDF sample.
5. Pack, update manifest/version metadata, and run all validations from the management skill.

Never infer ECCV categories from titles, abstracts, or the conference name.
