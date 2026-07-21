---
name: extract-rss-metadata
description: "Extract, normalize, verify, and publish Robotics: Science and Systems proceedings metadata from roboticsproceedings.org. Use when adding a new RSS year to aPaper Cloud or repairing an existing RSS pack."
---

# Extract RSS Metadata

## Source contract

- Use the official `roboticsproceedings.org/rssNN/` proceedings directory.
- Preserve each official paper page, HTTPS PDF URL, ordered authors, abstract, date, and DOI.
- Rewrite the publisher's legacy `http://www.roboticsproceedings.org/` PDF metadata to the equivalent HTTPS origin.
- Leave categories and `source_group` empty because the proceedings do not publish a complete per-paper topic or track taxonomy.
- Leave ISSN empty; do not substitute the proceedings ISBN.

Verified editions:

- 2025: `rss21`, 163 papers
- 2024: `rss20`, 134 papers

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm the requested year has a final official RSS proceedings directory and count its unique `pNNN.html` entries.
3. Run `scripts/fetch_rss_proceedings.py --series rssNN --year <year>` with a persistent cache directory.
4. Normalize with `import-json` using `venue_id=rss` and `edition_id=rss:<year>`.
5. Verify a deterministic PDF sample, pack the JSONL, update the Manifest, and run the management Skill validations.

Do not derive paper categories from the title, abstract, or conference name.
