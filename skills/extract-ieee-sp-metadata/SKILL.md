---
name: extract-ieee-sp-metadata
description: Extract, normalize, verify, and publish one IEEE Symposium on Security and Privacy year to aPaper Cloud. Use when the official accepted-paper or proceedings list changes or IEEE S&P metadata needs repair.
---

# Extract IEEE S&P Metadata

## Source contract

- Use the official IEEE Security and Privacy symposium accepted-papers/program pages and IEEE Computer Society proceedings metadata where publicly accessible.
- Display and store the venue ID as `ieee_sp` but the user-facing short name as `IEEE S&P`; never expose `IEEE_SP` as the conference label.
- Preserve the official paper/DOI landing page. Store a PDF URL only after verifying a real PDF response; exact-title author manuscripts may be used only with provenance retained.
- Use ISSN `1081-6011` for the symposium proceedings where applicable.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the official accepted-paper list is final for the requested year; keep an incomplete list `partial`.
3. Parse title, ordered authors, abstract, DOI, landing URL, publication date, and any official session/track with bounded concurrency and a resume cache.
4. Normalize to `venue_id=ieee_sp` and `edition_id=ieee_sp:<year>`; use `source_group` only for publisher-defined groupings.
5. Verify counts, duplicate IDs, required fields, and a deterministic PDF sample. Do not treat a browser/traffic-review page as a PDF.
6. Pack, update manifest/version metadata, and run all validations from the management skill.

If direct PDF access is restricted, keep the official landing link and let the App use its source-limitation dialog.
