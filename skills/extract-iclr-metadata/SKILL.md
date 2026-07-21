---
name: extract-iclr-metadata
description: Extract, normalize, verify, and publish one ICLR year to aPaper Cloud. Use when adding or refreshing an ICLR edition, replacing the temporary Supabase bridge, or repairing OpenReview metadata and PDF links.
---

# Extract ICLR Metadata

## Source contract

- Use the official OpenReview group `ICLR.cc/<year>/Conference` and its API notes.
- Include only papers with a final accepted venue/decision. Do not treat blind submissions as accepted papers.
- Preserve the OpenReview forum URL as `landing_url` and `provenance_url`.
- Derive `https://openreview.net/pdf?id=<forum_id>` only as a candidate. Keep it in `pdf_url` only after it returns a real `%PDF-` response rather than a challenge page.
- Preserve author-provided keywords as categories without local semantic translation or inference. ICLR display translation happens later in the App workflow.
- ICLR has no fixed proceedings ISSN.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md` and its temporary-channel document.
2. Fetch accepted notes with bounded pagination and save the raw response outside the repository for resume/debugging.
3. Normalize required fields to JSONL for `venue_id=iclr` and `edition_id=iclr:<year>`; record acceptance type as an official `source_group` when OpenReview exposes it.
4. Prefer publisher-owned data. Use `../manage-apaper-cloud-metadata/scripts/import_reference_supabase_temporary.py` only as an explicitly marked bridge, never as an App runtime dependency.
5. Verify required metadata, duplicate IDs, and a deterministic PDF sample. Use `partial` when challenge-protected PDFs cannot be verified.
6. Pack with `cargo run --quiet --manifest-path apaper-cloud/Cargo.toml -- pack ...`, update the exact manifest values, run `update_version.py`, and execute the three validation commands in the management skill.

Never commit OpenReview credentials, Supabase credentials, raw API dumps, or PDFs.
