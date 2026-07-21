---
name: extract-acl-metadata
description: Extract, normalize, verify, and publish one ACL proceedings year to aPaper Cloud. Use when ACL Anthology publishes a new annual meeting or ACL track metadata needs refresh.
---

# Extract ACL Metadata

## Source contract

- Use the official ACL Anthology repository XML for `<year>.acl.xml` plus `<year>.findings.xml` when present.
- Run the repository importer in `apaper-cloud`: `ingest-acl --input ... --venue acl --edition acl:<year> --year <year> --output ...`.
- Preserve the Anthology paper URL and PDF URL. Map Anthology volumes such as long, short, findings, demo, industry, SRW, and tutorials to `source_group`.
- Use ISSN `0736-587X` for ACL proceedings where the local library field applies.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Sparse-checkout or download only the required official XML files at a recorded ACL Anthology commit.
3. Run `cargo run --quiet --manifest-path apaper-cloud/Cargo.toml -- ingest-acl` with every official ACL/Findings input for that year.
4. Review skipped incomplete entries, duplicate IDs, track counts, and exact total against the source XML.
5. Verify a deterministic PDF sample with `../manage-apaper-cloud-metadata/scripts/verify_pdf_sample.py`.
6. Pack, update exact manifest values, run `update_version.py`, and execute all validations from the management skill.

Do not include workshops or co-located venues in the ACL annual-meeting edition unless explicitly requested.
