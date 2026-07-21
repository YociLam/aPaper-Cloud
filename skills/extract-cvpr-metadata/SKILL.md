---
name: extract-cvpr-metadata
description: Extract, normalize, verify, and publish one CVPR year to aPaper Cloud. Use when CVF publishes a new CVPR proceedings year or an existing CVPR metadata pack needs repair.
---

# Extract CVPR Metadata

## Source contract

- Use CVF Open Access as the authoritative paper source. Run `../manage-apaper-cloud-metadata/scripts/fetch_cvf_openaccess.py` against the official year day indexes.
- Preserve CVF HTML and PDF URLs. CVF does not provide a complete per-paper topic taxonomy, so leave `source_group` empty unless a future official track exists.
- Leave `categories` empty because CVF does not publish a complete, reliable per-paper topic taxonomy.
- Prefer online proceedings ISSN `2575-7075` for library metadata.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Fetch every official day index (and an official Findings collection when the requested year exposes one) with a resume cache and bounded concurrency.
3. Normalize official metadata to `venue_id=cvpr` and `edition_id=cvpr:<year>` with empty categories unless CVF adds an official paper-level taxonomy.
4. Verify a deterministic PDF sample, pack, update exact manifest metadata, update `version.json`, and run all validations from the management skill.

Never infer CVPR categories from titles, abstracts, community subsets, or the conference name.
