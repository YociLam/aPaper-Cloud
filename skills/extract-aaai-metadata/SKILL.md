---
name: extract-aaai-metadata
description: Extract, normalize, verify, and publish one AAAI proceedings year to aPaper Cloud. Use when the official AAAI OJS proceedings release a new volume or AAAI subjects and tracks need refresh.
---

# Extract AAAI Metadata

## Source contract

- Use the official AAAI OJS proceedings issue and article pages.
- Preserve the OJS article page as provenance and the publisher PDF link.
- Map the OJS section or technical track to `source_group`.
- When an article exposes `DC.Subject`, attach those exact subjects with `../manage-apaper-cloud-metadata/scripts/enrich_aaai_subjects.py`; do not infer replacements when the field is absent.
- Prefer online ISSN `2374-3468` for library metadata.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm all proceedings issues/sections belonging to the requested AAAI year; exclude workshops and unrelated journal issues unless requested.
3. Crawl issue pagination with a resume cache, then parse citation metadata, abstract, PDF, DOI, OJS section, and dates.
4. Normalize to `venue_id=aaai` and `edition_id=aaai:<year>`; enrich exact OJS subjects when available.
5. Verify counts, unique IDs, required fields, and a deterministic PDF sample.
6. Pack, update manifest and version files, and run all validations from the management skill.

Do not copy a technical-track label into every paper category when OJS provides no per-paper subject.
