---
name: extract-plos-climate-metadata
description: Extract licensed published PLOS Climate journal articles into aPaper annual metadata packs; use for a bounded new collection or publisher-backed refresh.
---

# PLOS Climate extraction

Read ../manage-apaper-cloud-metadata/SKILL.md and ../../docs/dp-new/E1-journal-contract.md. Scope: https://journals.plos.org/climate/s/journal-information. Verified eISSN 2767-3200; publisher Public Library of Science. Reviewed FORD mapping: oecd:ford:1.5. OECD defines fields, not this journal assignment.

Run `python3 ../manage-apaper-cloud-metadata/scripts/fetch_journal_collection.py --source plos_climate --year 2026 --cutoff <frozen-UTC> --output <task-output-directory>` from this Skill directory. Publisher-deposited Crossref journal works are build-time input, with terminal cursor, stable DOI and fixed publication filter. PLOS publisher Solr, queried by the verified eISSN, supplies the independent identity set and native article types.

Included types: Research Article, Review, Systematic Review. Never include front matter, corrections, retractions, news or known updated/retracted works as new recommendations. Retain exclusion IDs and reasons. Only effective article-level CC BY or CC0 is admitted. NC/ND licenses are explicit exclusions; absent license or abstract stays unresolved, never invented. Preserve ordered authors, title normalization, DOI, actual volume/issue/page/article number, online date and issue date separately. Online date precedes fallback issued date; no deposit timestamp as publication date. Annual partition is not a publisher volume.

Shared adapter has a 32 MiB response ceiling, complete JSON/HTML checks, terminal empty page and invariant unique identity accounting. No challenges bypass or credentials. A truncated response, changing count, duplicate DOI or zero admitted records is a failure. Inspect reconciliation.json: discovered = admitted + excluded + unresolved; current cutoff completeness is distinct from full-year completeness.

Use actual `cargo run -- pack --input <output>/plos_climate.jsonl --output public/v1/conferences/packs/plos_climate/2026.jsonl.zst`. Add only to `journals`, with journal identity and coverage, then regenerate version once after final manifest edit. Run validate-site, focused tests and deterministic `verify_pdf_sample.py` on the admitted pack input. PDFs stay outside repositories. Pack SHA/count/size come from commands, never guesses. Validate this Skill with the skill-creator quick_validate.py. No publishing is authorized by this extraction task.

A known failed PDF sample is stored as `<output>/pdf-checks.json` keyed by DOI, with exact URL, status and reason. Re-extraction clears only that matched failed URL, retains metadata, and never claims whole-pack PDF success. OUP 403 must remain a blocked sample; do not bypass its access controls.
