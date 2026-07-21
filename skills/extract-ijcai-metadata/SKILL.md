---
name: extract-ijcai-metadata
description: Extract, normalize, verify, and publish one IJCAI proceedings year to aPaper Cloud. Use when IJCAI releases a new proceedings index or subject-area mappings need repair.
---

# Extract IJCAI Metadata

## Source contract

- Use the official `ijcai.org/proceedings/<year>` index and paper pages.
- Preserve the official paper page and PDF URL.
- Map the official subject-area hierarchy to `source_group` and `categories`; keep the broad official category before more specific descendants.
- When multiple labels share a common parent such as Computer Vision, retain the hierarchy instead of translating every descendant into the same broad label.
- Use ISSN `1045-0823` for the IJCAI proceedings series where applicable.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Enumerate the complete official index and capture its subject-area grouping without relying on display order alone.
3. Parse title, authors, abstract, official page/PDF, DOI when present, dates, and subject hierarchy.
4. Normalize to `venue_id=ijcai` and `edition_id=ijcai:<year>` with stable official IDs.
5. Audit category hierarchy, duplicate translations, counts, and a deterministic PDF sample.
6. Pack, update exact manifest metadata, update `version.json`, and run all validations from the management skill.

Do not flatten distinct official child topics into repeated copies of one translated parent label.
