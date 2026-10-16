# Ubik — Semantic meaning and hierarchical categorization (2026-10-14)

## Product goal
Ubik **does not need to adjudicate ultimate factual truth** to be useful. It must understand what a source says, group sources about the same event, represent meaningful relations among statements, and assign **general-to-specific categories** without false specificity. A later human+AI synthesis preserves provenance and uncertainty.

## Distinct operations
1. **Source acquisition**: text/abstract and original URL, timestamps, language, source metadata.
2. **Candidate discovery**: multilingual E5 embeddings and metadata shortlist; same topic is not necessarily same event.
3. **LLM meaning adjudication**: event identity and relationships such as restates, adds detail, context, updates, supports, challenges, contrasts perspective. Every proposal includes verbatim evidence from each source. Contract: `ingestion/semantic_relation_contract.py`.
4. **Hierarchical taxonomy**: general subject -> domain -> subdomain -> specific theme, with 1–4 levels, abstention when evidence is insufficient. Contract: `ingestion/hierarchical_category_contract.py`.
5. **Source-grounded synthesis**: report convergence, differences and open questions without conflating truth and semantic compatibility.

## Example (illustrative, not model output)
An article about a European climate satellite might receive `Science > Space > Earth observation`. Another about a different satellite may share categories but not event identity. An article reporting a launch and one discussing a later instrument failure could be an event development, not a contradiction.

## Current implementation
- Validation modules and unit tests are committed on `develop/ubik-core`; CI runs tests.
- Prior RSS experiment generated 24 NLI statement pairs and a blinded annotation CSV; **no independently adjudicated gold labels yet**.
- LLM API execution, model comparison, automatic taxonomy inference, end-to-end publication and live article merging are **not implemented by these contracts**.
- Source quote presence checks prevent fabricated quotations in accepted proposals, but **do not prove semantic correctness or taxonomy quality**.
- Existing taxonomy pilot covers 400 documents and 29 taxonomy paths; prior fine-grained abstention was high, motivating hierarchical partial labeling.

## Next measurable experiment
Freeze a source snapshot. Evaluate on identical documents:
A. existing embedding + heuristic + NLI baseline;
B. embedding shortlist + pretrained reranker;
C. embedding shortlist + affordable general LLM producing structured relation and taxonomy proposals.

Independently annotate event identity, semantic relation and category path. Track precision/recall, false merges, taxonomy precision by depth, abstention by depth, evidence quote validity, per-language slices, latency and actual API spend. Prefer specific labels only when supported; allow general-only categories.

## Safety and deployment
No automatic merge, truth verdict or publication until held-out performance is measured. Record model/version, prompt, provenance, reviewer agreement and costs. Integrate with existing Supabase/Vercel architecture; do not modify main.


## Correzione strategica — 16 ottobre 2026

Le gerarchie libere generate per ogni singolo documento sono ora un **baseline sperimentale, non la strategia desiderata**. Preferire assegnazione a topic curati, tag normalizzati, nuclei rari e card multi-fonte su una singola notizia. Documenti fuori topic rimangono nel feed generale. Le esecuzioni OpenRouter su Europe PMC, inclusi 20 documenti con 6/20 classificazioni accettate e 14 errori di citazione letterale, sono registrate in [UBIK_DECISION_RECORD_2026-10-16.md](UBIK_DECISION_RECORD_2026-10-16.md). Distinguere qualità della gerarchia, controllo verbatim e coerenza del vocabolario condiviso.
