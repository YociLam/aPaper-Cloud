---
name: extract-colt-metadata
description: Extract, normalize, verify, and publish COLT proceedings metadata from the final PMLR volume. Use when adding a new Conference on Learning Theory year to aPaper Cloud or repairing an existing COLT pack.
---

# Extract COLT Metadata

## Source contract

- Use the final Proceedings of Machine Learning Research volume for the requested year.
- Preserve the PMLR abstract page, publisher PDF URL, ordered authors, abstract, date, and DOI when present.
- Leave categories and `source_group` empty unless the final proceedings publish a real per-paper track or topic.
- Treat PMLR ISSN `2640-3498` as proceedings-series metadata when importing a paper into the local library.

Verified volumes:

- 2026: `v336`
- 2025: `v291`

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the requested year has a final PMLR volume.
3. Run the shared PMLR importer with `--expected-title-fragment "Conference on Learning Theory"`.
4. Normalize with `import-json` using `venue_id=colt` and `edition_id=colt:<year>`.
5. Verify a deterministic PDF sample, pack the JSONL, update the manifest, and run the management Skill validations.

Do not infer theoretical-learning subtopics from titles or abstracts.
