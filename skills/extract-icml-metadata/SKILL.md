---
name: extract-icml-metadata
description: Extract, normalize, verify, and publish one ICML proceedings year to aPaper Cloud. Use when a final PMLR ICML volume appears or an existing ICML metadata pack needs repair.
---

# Extract ICML Metadata

## Source contract

- Use the final ICML volume on Proceedings of Machine Learning Research, not the conference schedule or an OpenReview submissions list.
- Preserve each PMLR paper HTML page as `landing_url` and `provenance_url`; use its publisher-provided PDF URL.
- Leave per-paper categories empty unless the final volume publishes a real track or topic. Do not write `ICML` as a category.
- Use proceedings ISSN `2640-3498` when mapping the paper into the local library.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the final PMLR volume and exact paper count. If no final volume exists, keep the edition `announced` or `cataloged` with no pack.
3. Fetch the volume index with bounded concurrency, then parse title, ordered authors, abstract, HTML URL, PDF URL, DOI when present, and publication date.
4. Normalize to `venue_id=icml`, `edition_id=icml:<year>`, and stable source-derived IDs.
5. Validate PDF headers using `../manage-apaper-cloud-metadata/scripts/verify_pdf_sample.py`. Slow responses may wait; HTTP denial, 404, or non-PDF content must not be published as a working PDF.
6. Pack, update manifest checksums and counts, run `update_version.py`, then run all validations from the management skill.

Do not publish a conference-announcement count as a completed PMLR pack.
