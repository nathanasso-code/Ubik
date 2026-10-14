# Ubik — First real semantic preselection evidence (2026-10-14)

## Evidence source
GitHub Actions run 38549026502, artifact 11885219881, `discovery/hybrid-event-review.json` and `discovery/llm-candidate-queue.json` on branch `develop/ubik-core`.

## Measured
- 400 source records in hybrid review.
- 100 input candidate pairs; 100 eligible pairs; 30 selected under the configured budget.
- The first ranked pair links BBC reporting about missiles near Riyadh and a Saudi strike on a Yemen fuel depot with Guardian reporting about oil depots in Yemen and missiles toward Saudi Aramco HQ (similarity 0.9235). This is a candidate for temporal/event relationship analysis, not an established equivalence.
- The second pair links Ars Technica and Guardian coverage of honeybee stingers pumping venom (similarity 0.9205), plausibly different descriptions of the same research, not yet adjudicated.
- Input records contain URL, title, description and preliminary taxonomy candidates, **not complete article text**. The BBC Yemen description is one sentence; insufficient for deep interpretation.

## Meaning of the experiment
This confirms the existing embedding + hybrid pipeline can supply cross-source candidates to a bounded review queue. It does **not** measure retrieval recall, semantic relation correctness, LLM performance or taxonomy accuracy.

## Execution blocker
No `UBIK_LLM_API_KEY` or `OPENAI_API_KEY` was available in the working runtime. Do not assume GitHub has a usable secret. No paid LLM API calls were made. The optional adapter is ready for an explicit HTTPS provider configuration.

## Next empirical milestone
1. Run CI readiness report on the 30 candidates and quantify missing text.
2. Acquire permitted full texts for a stratified subset; keep original URL and quoted evidence.
3. Run 5–10 pairs against a low-cost LLM with explicit budget; store outputs, tokens and latency.
4. Independently assess event identity, relation and hierarchical categories; compare against existing hybrid/NLI baseline.
5. Include isolated novel articles as a separate route.

No production publishing or automatic merging until evaluated.
