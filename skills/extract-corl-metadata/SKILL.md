---
name: extract-corl-metadata
description: Extract, normalize, verify, and publish CoRL proceedings metadata from the final PMLR volume. Use when adding a new Conference on Robot Learning year to aPaper Cloud or repairing an existing CoRL pack.
---

# Extract CoRL Metadata

## Source contract

- Use the final Proceedings of Machine Learning Research volume for the requested year.
- Preserve the PMLR abstract page, publisher PDF URL, ordered authors, abstract, date, and DOI when present.
- Leave categories and `source_group` empty unless the final proceedings publish a real per-paper track or topic.
- Treat PMLR ISSN `2640-3498` as proceedings-series metadata when importing a paper into the local library.

Verified volumes:

- 2025: `v305`
- 2024: `v270`

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the requested year has a final PMLR volume; do not substitute an OpenReview submission list.
3. Run the shared PMLR importer with `--expected-title-fragment "Conference on Robot Learning"`.
4. Normalize with `import-json` using `venue_id=corl` and `edition_id=corl:<year>`.
5. Verify a deterministic PDF sample, pack the JSONL, update the manifest, and run the management Skill validations.

Do not turn the broad robotics domain into a per-paper category.
