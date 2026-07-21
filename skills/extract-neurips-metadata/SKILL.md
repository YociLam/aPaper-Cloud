---
name: extract-neurips-metadata
description: Extract, normalize, verify, and publish one NeurIPS proceedings year to aPaper Cloud. Use when the official NeurIPS proceedings site releases a new year or an existing NeurIPS pack needs correction.
---

# Extract NeurIPS Metadata

## Source contract

- Use `proceedings.neurips.cc` for the requested year.
- Preserve the official abstract page and PDF link. Record an official track such as Main Conference, Datasets and Benchmarks, or Competition as `source_group` when the proceedings distinguishes it.
- Do not infer topics from titles or abstracts and do not use `NeurIPS` as a category.
- Use ISSN `1049-5258` only where the local library field represents the Advances in Neural Information Processing Systems series.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Enumerate the official year index and all official track indexes with bounded pagination/concurrency.
3. Parse title, authors, abstract, abstract URL, PDF URL, and track; deduplicate by official paper hash/ID.
4. Normalize to `venue_id=neurips` and `edition_id=neurips:<year>`.
5. Verify required fields and a deterministic PDF sample. Keep an unverified edition unavailable rather than substituting arXiv broadly.
6. Pack, update exact manifest metadata, update `version.json`, and run all validations from the management skill.

Never use an OpenReview submission list as a substitute for the final proceedings.
