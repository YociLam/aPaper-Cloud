---
name: extract-emnlp-metadata
description: Extract, normalize, verify, and publish one EMNLP proceedings year to aPaper Cloud. Use when ACL Anthology publishes a new EMNLP meeting or EMNLP volume metadata needs refresh.
---

# Extract EMNLP Metadata

## Source contract

- Use the official ACL Anthology repository XML for `<year>.emnlp.xml` and `<year>.findings-emnlp.xml` when present.
- Preserve Anthology landing and PDF URLs.
- Map official volumes such as main, findings, demo, industry, and system demonstrations to `source_group`.
- Use ISSN `1932-1956` where the local library field represents the EMNLP proceedings series.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Pin the ACL Anthology repository commit and acquire only the requested year's EMNLP XML files.
3. Run the `apaper-cloud` `ingest-acl` command with `--venue emnlp --edition emnlp:<year>` and every official EMNLP/Findings input.
4. Audit skipped records, duplicate IDs, volume counts, required fields, and exact source total.
5. Verify a deterministic PDF sample.
6. Pack, update manifest/version metadata, and run all validations from the management skill.

Keep workshops and unrelated ACL Anthology collections outside the EMNLP edition.
