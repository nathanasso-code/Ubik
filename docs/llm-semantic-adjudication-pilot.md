# LLM semantic adjudication pilot

Design: embedding retrieval -> shortlist -> LLM semantic adjudication -> provenance checks -> optional verification. This pilot does not automatically merge or publish.

## API-agnostic JSON contract

Input: source documents with stable ids, URLs, publication dates, language, full accessible text or abstract, and quoted spans.

Output per candidate pair:
```json
{"document_a_id":"a","document_b_id":"b","same_event":"yes|no|uncertain","relation":"same_report|update|complementary|different_event|uncertain","time_relation":"same_stage|before_after|unknown","claims":[{"claim_a":"...","claim_b":"...","relation":"equivalent|entails|compatible|contradicts|unknown","source_a_quote":"...","source_b_quote":"..."}],"requires_review":true}
```

Rules: distinguish event identity from statement relationship and truth. Never assert a contradiction from missing or temporally incompatible context. Exact quoted evidence must occur in supplied source text. No automatic publishing or merging. Treat malformed or ungrounded responses as abstentions.

## Benchmarks
Compare existing E5+NLI, E5+Qwen reranker, and E5+small general LLM on the same frozen independently labeled sample. Measure event pair F1, false merges, grounded claim precision, abstentions, cost and latency. Do not score the model-selected 24 audit pairs as unbiased accuracy.

## Economics
Estimate actual input/output token counts per stage, cache reuse, retries, and extra web retrieval separately. Never compare provider models on price alone.

## Rollout
Phase 1: offline comparison and review. Phase 2: shadow-mode decisions. Phase 3: human-confirmed merges. Phase 4: threshold-based automation only after measured false-merge acceptability.
