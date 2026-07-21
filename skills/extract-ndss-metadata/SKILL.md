---
name: extract-ndss-metadata
description: Extract, normalize, verify, and publish one NDSS Symposium proceedings year to aPaper Cloud. Use when the official NDSS paper collection releases a new year or NDSS URLs and counts need repair.
---

# Extract NDSS Metadata

## Source contract

- Use the official NDSS Symposium program/paper pages for the requested year.
- Preserve each NDSS paper page and its official PDF URL.
- Map official program sessions to `source_group` only when the NDSS site publishes a stable mapping; otherwise leave paper topics empty.
- NDSS has no fixed proceedings ISSN; leave ISSN empty unless the requested edition proves one explicitly.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Enumerate the complete official year collection with bounded pagination/concurrency and a resume cache.
3. Parse title, authors, abstract, paper URL, PDF URL, DOI when present, dates, and official session.
4. Normalize to `venue_id=ndss`, `edition_id=ndss:<year>`, and stable official slug/ID-derived identifiers.
5. Audit exact count, duplicates, required fields, and a deterministic PDF sample; reject HTML/challenge content returned from PDF URLs.
6. Pack, update manifest/version metadata, and run all validations from the management skill.

Do not fill missing topics with a shared `Security` category.
