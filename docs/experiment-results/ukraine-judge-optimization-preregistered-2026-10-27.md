# Ukraine judge optimization — preregistration (2026-10-27)

## Closed decisions
- v4 Sonnet extraction and judge remain baseline; uniform composer retained.
- v5 Sonnet not promoted: 2.2003x baseline cost.
- DeepSeek V3.2 not promoted: false equivalence between S188:e3 and S387:e3. Reference unchanged.
- Qwen and Gemini excluded.

## Frozen data and ceiling
- Exact v5 Sonnet extraction artifact 12719538526 (38 events), exact v5 judge artifact 12725256478 (131 ordered judgments). No candidate regeneration.
- v4 baseline $0.335854; two-model ceiling $0.671708 including $0.149988 frozen extraction, judge calls, retries and adjudication where applicable. Every stage reports actual API cost, and missing cost data blocks economic promotion.
- Common composer, no changes to frozen gold, no retroactive promotion.
- One identical retry for malformed judge output, then operational uncertain with invalid_after_retry; 7 or more final invalids => partial, never promoted; failed blocking pairs => unproven.

## Arm 1: Sonnet concise
- Exact same model as v5 (`anthropic/claude-sonnet-5.5`); preserve default reasoning mode and model configuration. Do not change thinking budget or introduce reasoning-effort parameters.
- Change only response format. Prompt frozen below, before execution. Each result must contain decision, direction, detail_conflicts, evidence (single brief sentence). No verbose explanation.
- Prompt caching only if provider supports it without changing model behavior; record cache reads/writes. Batch only if provider supports it with the same model and reproducible API responses; otherwise synchronous sequential.
- Strictly record provider model, usage, actual billed cost and all retries.

### Frozen concise prompt
Judge only the two supplied cross-source events, using their evidence. Output JSON with decision equivalent|distinct|uncertain|part_of, direction left_part_of_right|right_part_of_left|null, detail_conflicts array, and evidence as exactly one short sentence grounded in the supplied evidence. Equivalent means same concrete act or fact, not merely common topic. part_of requires a supported component-of relation, not mere reaction or proximity. Keep EU diesel supply agreement and US suspension of new sanctions distinct; generic sanctions easing may be ambiguous, so use uncertain if evidence insufficient. Distinguish Trump announcement from asserted agreement. Never invent missing evidence. Do not output extended reasoning.

## Arm 2: DeepSeek V4.1 Flash
- Exact original v5 judge prompt unchanged. Same ordered 131 pairs.
- A single explicitly selected provider with list price, no fallbacks, provider JSON schema support verified before paid run; fixed reasoning mode and separate reasoning-token audit. Cost from API responses, not price estimates.
- Do not run if model/provider identity or structured-output capability cannot be verified.

## Comparison and promotion
- Pairwise automatic comparison against original Sonnet judgments.
- All disagreements rejudged with original Sonnet configuration to distinguish instability from error; freeze disagreement list before adjudication.
- Recompose and weighted-evaluate only arms that pass blocking controls: no A diesel/B executive-order equivalence or structural merger, no new weight-3 errors, no false S188:e3/S387:e3 equivalence.
- Cascade candidate: best eligible DeepSeek on all pairs; winning Sonnet format rejudges every non-distinct DeepSeek pair. Separately audit Sonnet-uncertain / DeepSeek-distinct pairs. Eligible only if no new weight-3 error, weighted error <= original v5 Sonnet judge and measured total cost <= $0.671708.
- Validate on a second independent cluster the hypothesis that DeepSeek-distinct never contradicts Sonnet-equivalent before any adoption. This is a hypothesis, not a fact.

## Parallel zero-cost analysis
- Align v4/v5 event IDs using extraction text, act/object/evidence alone, blind to judgments; freeze mapping before evaluation. Attribute differences separately to extraction, candidate retrieval and judge. Do not use LLM calls.

## Later
- AI corpus: topic perimeter, light reference, final page of summaries. Not part of this execution.
