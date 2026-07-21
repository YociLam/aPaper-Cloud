---
name: extract-osdi-metadata
description: Extract, normalize, verify, and publish one OSDI technical-program year to aPaper Cloud. Use when USENIX publishes a new OSDI program or official session mappings need refresh.
---

# Extract OSDI Metadata

## Source contract

- Use the official USENIX OSDI technical-sessions page and presentation pages.
- Preserve USENIX landing and PDF URLs.
- Run `../manage-apaper-cloud-metadata/scripts/enrich_osdi_sessions.py --year <year>` and require every paper page to map to an official technical-session name before publishing that grouping.
- Use ISSN `2575-8411` for the OSDI proceedings where applicable.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the requested year's technical program is complete; a partial program remains `partial` or `cataloged`.
3. Enumerate presentation pages with bounded concurrency and parse citation metadata, abstract, PDF, DOI when present, and dates.
4. Normalize to `venue_id=osdi`, `edition_id=osdi:<year>`, then enrich exact official session groups.
5. Verify every session mapping, required fields, unique IDs, total count, and a deterministic PDF sample.
6. Pack, update manifest/version metadata, and run all validations from the management skill.

Do not infer operating-systems topics when a session name is unavailable.
