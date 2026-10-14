---
name: extract-ijcai-metadata
description: Extract final IJCAI proceedings metadata and publisher subjects for aPaper, preserving indexed collection scope.
---

# Extract IJCAI metadata

Read ../manage-apaper-cloud-metadata/SKILL.md. The annual publisher proceedings are
https://www.ijcai.org/proceedings/<year>/; 2026 is verified final. Index sections/subsections
contain paper_wrapper IDs and Details links. Include every indexed contribution (main,
special tracks, sister-conference summaries and demonstrations) consistent with the existing
proceedings collection; exclude front matter without a paper ID. Describe this scope explicitly.

Run `../manage-apaper-cloud-metadata/scripts/fetch_ijcai_proceedings.py --year <year>
--cache-dir <outside-repo> --output <json>`. It uses four workers and one complete index;
no separate pagination. Review unique ID and official link counts before import.
Use `ijcai-<year>-<numeric publisher ID>` identities. Detail citation metadata supplies
ordered authors, title, date, DOI, PDF URL. The plain abstract and per-paper topic labels
come from the detail page; source_group retains the indexed official subject heading, or the enclosing official track
when no subject heading is supplied. Keep subject_area and track kinds distinct.
Do not invent abstracts/dates or infer categories. A failed detail aborts extraction rather
than silently reducing the collection. Keep HTML caches outside the repository.

Normalize using `import-json --venue ijcai --edition ijcai:<year> --year <year>`, inspect
skipped counts, verify a deterministic PDF sample including each included track, then pack
under `public/v1/conferences/packs/ijcai/<year>.jsonl.zst`. Record sample coverage honestly;
PDF bodies never enter the repository. Update counts, availability, bytes, checksum and
pack_version only from actual output. Regenerate version.json and run management validators
and adapter fixtures after final candidate edits. Publication requires separate authorization.
