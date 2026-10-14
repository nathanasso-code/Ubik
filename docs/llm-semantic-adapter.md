# Ubik — LLM semantic adapter: implementation status
Date: 2026-10-14. Branch: develop/ubik-core.

The adapter in `ingestion/llm_semantic_adapter.py` consumes `llm-candidate-queue.json` and the existing hybrid event corpus. It preserves source text, prepares prompts for an OpenAI-compatible JSON chat endpoint, and checks returned event relations, semantic relations and general-to-specific categories against literal quotes from both source documents.

## Offline CI (default)
`python -m ingestion.llm_semantic_adapter --queue data/discovery/llm-candidate-queue.json --hybrid data/discovery/hybrid-event-review.json --output data/discovery/llm-semantic-readiness.json --limit 30`
No API calls, no model analysis and no cost. Output reports ready/missing-source/missing-text counts.

## Optional paid test (NOT run automatically)
Set `UBIK_LLM_ENDPOINT` to a trusted HTTPS OpenAI-compatible `/chat/completions` URL, `UBIK_LLM_MODEL` and `UBIK_LLM_API_KEY` via secrets. Add `--execute --limit 5` to explicitly run inference. Do not put credentials in repository files or logs. Verify provider support for JSON response format and provider billing.

## Interpretation
Successful quote validation means only that quoted substrings occur in the supplied text. It does not prove a relation or category is correct. The output remains review-only. API errors are recorded by type without leaking secrets. No automatic merging or publishing.

## Current limitations and next experiment
Existing hybrid snapshots may include only titles or abstracts, not full article bodies; this can severely limit analysis. CI cannot measure LLM quality in dry-run. Next: run on a small frozen source-linked corpus with accessible text, compare predictions against independently reviewed relations and category paths, measure cost/latency and false merges. Add novelty lane for unmatched articles.
