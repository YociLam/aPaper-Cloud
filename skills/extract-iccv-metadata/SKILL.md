---
name: extract-iccv-metadata
description: Extract, normalize, verify, and publish ICCV proceedings metadata from CVF Open Access. Use when adding a new ICCV edition to aPaper Cloud or repairing an existing ICCV pack.
---

# Extract ICCV Metadata

## Source contract

- Use the official CVF Open Access repository for the requested ICCV edition.
- Preserve each CVF paper page, official PDF URL, ordered authors, abstract, and publication year.
- Leave categories and `source_group` empty because CVF Open Access does not provide a complete per-paper topic taxonomy for ICCV.
- Treat ICCV as a biennial conference; select the most recent published editions rather than assuming consecutive calendar years.

Verified editions:

- 2025: `https://openaccess.thecvf.com/ICCV2025?day=all`
- 2023: `https://openaccess.thecvf.com/ICCV2023?day=all`

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Download the official `day=all` index and count unique paper detail links.
3. Run `../manage-apaper-cloud-metadata/scripts/fetch_cvf_openaccess.py --conference ICCV` with bounded concurrency and a persistent cache directory.
4. Normalize with `import-json` using `venue_id=iccv` and `edition_id=iccv:<year>`.
5. Verify a deterministic PDF sample, pack the JSONL, update the manifest, and run the management Skill validations.

Do not infer categories from titles, abstracts, or third-party paper lists.
