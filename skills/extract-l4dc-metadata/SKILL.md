---
name: extract-l4dc-metadata
description: Extract and verify L4DC final PMLR proceedings for aPaper metadata packs. Use for a new edition or a publisher-backed refresh.
---

# Extract L4DC metadata

Read ../manage-apaper-cloud-metadata/SKILL.md for candidate validation and release boundaries.

## Verified source and scope

The publisher index https://proceedings.mlr.press/ identifies the latest verified edition as
2026, volume v331: https://proceedings.mlr.press/v331/.
The conference/meeting is annual; always recheck the index before selecting a newer volume.
Include PMLR annual conference proceedings; excludes preface and separate workshop collections. Do not substitute an accepted-submission list for final proceedings.

## Execute

1. Supply volume, venue `l4dc`, integer year and expected container-title fragment `Learning for Dynamics and Control`
   to `../manage-apaper-cloud-metadata/scripts/fetch_pmlr_volume.py`.
   The publisher-maintained `mlresearch/<volume>` gh-pages archive contains all `_posts/*.md`;
   it is the acquisition input only, never an App runtime fallback. There is no page cursor.
   Check its unique paper-ID set against the public volume's HTML landing links.
2. The adapter preserves YAML author order, title, abstract, publisher date, DOI when supplied,
   and the exact abstract-page and PDF URLs. Native categories are absent, so leave them empty.
   Exclude prefaces explicitly. Fail on missing title, authors, abstract, PDF, date, or mismatched
   collection; do not invent fields. Stable IDs are publisher paper IDs, unchanged across refresh.
3. Run the repository `import-json --venue l4dc --edition l4dc:<year> --year <year>` command.
   Its shared title normalizer converts source markup to plain Unicode; the packer rejects
   unsupported markup. Check exact record count and no skipped incomplete records.
4. Run `verify_pdf_sample.py --input <jsonl>` using deterministic sampling. Verify HTTPS and
   `%PDF-` bytes; a login/challenge page is a failure. Report sampled/verified/failed counts,
   not whole-pack PDF coverage. Keep downloaded bytes and caches outside the repository.
5. Use `pack --input <jsonl> --output public/v1/conferences/packs/l4dc/<year>.jsonl.zst`;
   take record count, bytes and SHA-256 from its output, add localized names and reviewed
   discipline IDs to the same manifest, and accurately set availability. Preserve existing
   record IDs; any removed ID requires a publisher collection-scope explanation.
6. Advance manifest version once for the candidate; regenerate version.json and run the
   release validator/tests after the final change. Production publication needs separate authorization.
