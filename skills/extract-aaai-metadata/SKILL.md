---
name: extract-aaai-metadata
description: Extract, normalize, verify, and publish one AAAI proceedings year to aPaper Cloud. Use when the official AAAI OJS proceedings release a new volume or AAAI subjects and tracks need refresh.
---

# Extract AAAI Metadata

## Source contract

- Use the official AAAI OJS proceedings issue and article pages.
- Preserve the OJS article page as provenance and the publisher PDF link.
- Map the OJS section or technical track to `source_group`.
- When an article exposes `DC.Subject`, attach those exact subjects with `../manage-apaper-cloud-metadata/scripts/enrich_aaai_subjects.py`; do not infer replacements when the field is absent.
- Prefer online ISSN `2374-3468` for library metadata.

## Workflow

1. Read `../manage-apaper-cloud-metadata/SKILL.md`.
2. Confirm all OAI sets belonging to the requested AAAI year; the standard aPaper AAAI pack includes only `AAAI Technical Track` records, matching prior years, and excludes IAAI, EAAI, demonstrations, student abstracts, consortium, journal, and special-track records unless the catalog scope is explicitly changed.
3. Fetch the official OAI-PMH sets with the resumable extractor. It requests each technical track independently so one long OJS pagination failure cannot invalidate the whole edition:

   ```sh
   python3 skills/extract-aaai-metadata/scripts/fetch_aaai_oai.py \
     --year <year> \
     --output /tmp/aaai-<year>.json \
     --cache-dir /tmp/apaper-aaai-<year>-oai
   ```

   The extractor parses abstract, PDF, DOI, official track, subjects, and dates directly from OAI-PMH. Keep the cache outside the repository.
4. Normalize to `venue_id=aaai` and `edition_id=aaai:<year>`; enrich exact OJS subjects when available.
5. Verify counts, unique IDs, required fields, and a deterministic PDF sample.
6. Pack, update manifest and version files, and run all validations from the management skill.

Do not copy a technical-track label into every paper category when OJS provides no per-paper subject.
