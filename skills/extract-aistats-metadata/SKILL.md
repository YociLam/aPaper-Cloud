---
name: extract-aistats-metadata
description: Extract, normalize, verify, and publish AISTATS proceedings metadata from the final PMLR volume. Use when adding a new AISTATS year to aPaper Cloud or repairing an existing AISTATS pack.
---

# Extract AISTATS Metadata

## Source contract

- Use the final Proceedings of Machine Learning Research volume for the requested year.
- Preserve the PMLR abstract page, publisher PDF URL, ordered authors, abstract, date, and DOI when present.
- Leave categories and `source_group` empty unless the final proceedings publish a real per-paper track or topic.
- Treat PMLR ISSN `2640-3498` as proceedings-series metadata when importing a paper into the local library.

Verified volumes:

- 2025: `v258`
- 2024: `v238`

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the requested year has a final PMLR volume; do not substitute an OpenReview submission list.
3. Run the shared PMLR importer with `--expected-title-fragment "Artificial Intelligence and Statistics"`.
4. Normalize with `import-json` using `venue_id=aistats` and `edition_id=aistats:<year>`.
5. Verify a deterministic PDF sample, pack the JSONL, update the manifest, and run the management Skill validations.

Keep an edition announced or cataloged when its final PMLR volume is not yet available.
