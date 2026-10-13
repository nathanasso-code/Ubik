# Ubik — Continuity increment: first empirical false-merge regression (2026-10-13)

## Verified starting point
The 120-body Wikinews experiment completed successfully in run [38354341166](https://github.com/nathanasso-code/Ubik/actions/runs/38354341166): 120 acquired documents, 600 sentence candidates, four title-similarity pairs, two multi-document groups, 117 card previews. 47 cards were unclassified, 39 Politics and Society, 23 Conflict and Security, six Health, one Economy, one Technology and Science. This is a single-publisher snapshot, not independently corroborated information or validated claims. The raw body content was not uploaded in the workflow artifact.

Two groups exposed false same-event conflation: (a) Caloundra soccer rounds 2, 3 and first win; (b) Mamdani's mayoral election and earlier Democratic primary. The title similarity grouping treated distinct events as interchangeable.

## Implemented on develop/ubik-core
- `ingestion/open_corpus_event_guard.py`: review-only deterministic guard marks visibly different sporting rounds and primaries versus general elections as related-but-distinct; ambiguous pairs abstain, never verify.
- `ingestion/open_corpus_analysis.py`: title-based grouping now consults the guard for each pair and when expanding groups; card metadata includes full source titles, cautious pair review outcomes and explicit lack of verified independence.
- `tests/test_open_corpus_event_guard.py` and regression added to `tests/test_open_corpus_experiment.py`.
- `.github/workflows/open-text-corpus-experiment.yml`: test both modules before the 120-body run.

This is an interim precision safeguard, **not** generalized entity-action-time extraction. It may reduce recall, and it does not establish that any remaining pairs represent the same event. Future candidate relations need source passage, event time, role, scope, negation and explicit editorial review.

## Next empirical priorities
1. Inspect newest 120-article workflow logs and artifact: check grouping change without pretending the result establishes semantic correctness.
2. Export privacy- and rights-conscious representative **short** claim examples with source URL, stable fingerprint, and extractive provenance (no full article bodies); audit whether extraction is actual reporting or boilerplate.
3. Establish an event-frame schema (actor/action/object/place/time/scope), initially review-only and abstention-first. Measure false merges and false separations on a blinded, annotated stratified sample.
4. Expand open-body source families (e.g. official institutions, public research records) through explicit per-source access and rights review. A domain is not an independent editorial origin and a license requires page-specific assessment.
5. Introduce genuinely informative event-specific extractive synthesis only when each phrase is traceable to exact source passages. Maintain no automatic verified/published state.

Keep `main`, production Supabase/Vercel, historic artifacts and topic-first navigation unchanged.
