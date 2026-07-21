---
name: extract-aamas-metadata
description: Extract, normalize, verify, and publish AAMAS proceedings metadata from the official IFAAMAS table of contents, Crossref DOI records, and official PDFs. Use when adding a new AAMAS year to aPaper Cloud or repairing an existing AAMAS pack.
---

# Extract AAMAS Metadata

## Source contract

- Use `ifaamas.org/Proceedings/aamas<year>/forms/contents.htm` as the exact paper-set and track boundary.
- Match Crossref prefix `10.65109` by normalized exact title when it supplies the abstract and DOI.
- When Crossref is incomplete, download the official IFAAMAS PDF with bounded concurrency and extract only an explicitly labeled `ABSTRACT` from its first two pages.
- Preserve publisher-defined tracks as `source_group`; never convert keywords or inferred subjects into categories.
- Omit records whose official PDF has no extractable abstract. Mark an edition `partial` when this makes the pack smaller than the official paper list.
- Leave ISSN empty because AAMAS proceedings do not expose a verified fixed series ISSN.

Verified editions:

- 2026: 641 official paper entries; 639 complete searchable records, so publish as `partial`
- 2025: 479 complete searchable records

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Download and inspect the official table of contents; exclude front matter by accepting only the edition's paper filename convention.
3. Run `scripts/fetch_aamas_proceedings.py --year <year>` with a persistent cache directory outside the repository and at most four workers.
4. Review every reported failure. Do not fill missing abstracts from titles, introductions, or an LLM.
5. Normalize with `import-json` using `venue_id=aamas` and `edition_id=aamas:<year>`.
6. Verify a deterministic PDF sample, pack the JSONL, update the Manifest, and run the management Skill validations.

Keep the pack metadata-only; never commit the cached PDFs.
