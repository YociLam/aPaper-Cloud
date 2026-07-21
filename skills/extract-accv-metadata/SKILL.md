---
name: extract-accv-metadata
description: Extract, normalize, verify, and publish ACCV proceedings metadata from CVF Open Access. Use when adding a new Asian Conference on Computer Vision edition to aPaper Cloud or repairing an existing ACCV pack.
---

# Extract ACCV Metadata

## Source contract

- Use the official CVF Open Access repository for the requested ACCV edition.
- Preserve each CVF paper page, official PDF URL, ordered authors, abstract, and publication year.
- Leave categories and `source_group` empty because CVF Open Access does not provide a complete per-paper topic taxonomy for ACCV.
- Treat ACCV as a biennial conference; select the most recent published editions rather than assuming consecutive calendar years.
- Use electronic LNCS ISSN `1611-3349` only when mapping the proceedings series into the local library.

Verified editions:

- 2024: `https://openaccess.thecvf.com/ACCV2024?day=all`
- 2022: `https://openaccess.thecvf.com/ACCV2022?day=all`

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Download the official `day=all` index and count unique paper detail links.
3. Run `../manage-apaper-cloud-metadata/scripts/fetch_cvf_openaccess.py --conference ACCV` with bounded concurrency and a persistent cache directory.
4. Normalize with `import-json` using `venue_id=accv` and `edition_id=accv:<year>`.
5. Verify a deterministic PDF sample, pack the JSONL, update the manifest, and run the management Skill validations.

Do not infer categories from titles, abstracts, or third-party paper lists.
