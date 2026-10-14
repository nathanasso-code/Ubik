# Ubik — Proprietary preselection and LLM escalation
Status: executable offline queue; no LLM API invoked.

The existing multilingual E5 embeddings and hybrid event heuristics supply candidate pairs. `ingestion/llm_candidate_router.py` ranks eligible pairs, prioritizes ambiguous semantic neighbors, deduplicates URLs and applies a configurable pair budget (default 30). It emits `data/discovery/llm-candidate-queue.json` in the global discovery workflow.

Example: `python -m ingestion.llm_candidate_router --hybrid data/discovery/hybrid-event-review.json --output data/discovery/llm-candidate-queue.json --budget 30`

This is **not** an accuracy score and does not assert event identity, relations or taxonomy. The queue's status is `queued_not_analyzed`. The new hierarchy contract and relation contract define how future LLM output should be validated; no provider has been connected or charged.

## Next implementation
Add an optional configurable LLM provider adapter in offline/shadow mode; pass both original source passages, metadata and category context; validate grounded quotes, event relations and general-to-specific categories; persist prompt/model/version/token usage; compare against baseline on frozen independently reviewed pairs. Maintain a separate novelty lane for isolated articles so high-value new events are not discarded.

## Risk controls
Avoid automatically merging based on ranking score. Prefer cached embeddings and bounded candidate count. Do not discard source text. Separate public interest from need for semantic analysis. Do not call paid APIs in CI without explicit cost controls.
