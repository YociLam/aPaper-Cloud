---
name: extract-sosp-metadata
description: Extract, normalize, verify, and publish one SOSP proceedings year to aPaper Cloud. Use when ACM publishes a new SOSP proceedings year, when replacing the temporary Supabase bridge, or when SOSP PDF provenance needs repair.
---

# Extract SOSP Metadata

## Source contract

- Prefer the official ACM Digital Library proceedings/DOI pages. Keep DOI landing pages as provenance.
- ACM challenge pages must not be stored as verified PDFs. Use a public publisher or exact-title open-access PDF only after `%PDF-` verification.
- Use `../manage-apaper-cloud-metadata/scripts/import_reference_supabase_temporary.py` only as a removable, marked build-time bridge when publisher acquisition is blocked.
- Do not assign ISSN `0163-5980` automatically; it belongs to the SIGOPS review/newsletter context and is not proof of a SOSP proceedings ISSN for every edition.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md` and `../manage-apaper-cloud-metadata/TEMPORARY_REFERENCE_SUPABASE_CHANNEL.md`.
2. Enumerate the exact SOSP proceedings year from publisher-owned pages and normalize DOI, title, authors, abstract, dates, and landing URL.
3. Preserve official sessions/tracks only when the proceedings publishes them; otherwise leave categories and `source_group` empty.
4. If the temporary bridge is unavoidable, retain `metadata_channel=temporary_reference_supabase_v1` and never copy its credentials.
5. Enrich only exact-title verified open-access PDFs, then audit counts and sample PDFs. Use `partial` when PDF coverage remains incomplete.
6. Pack, update manifest/version metadata, and run all validations from the management skill.

Never make the App query Supabase or ACM at runtime to obtain the metadata pack.
