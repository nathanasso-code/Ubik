# Ubik v5.1 — Ukraine diagnostic protocol (preregistered)

Registered 2026-10-29, before any v5.1 model call. Owner of execution: Claude. This file is the
preregistration; the shared Claude Doc "Ubik — Prompt v5: indicazioni dal campione e glossario"
holds the reasoning in Italian.

## 1. What changes and what does not

v5.1 changes only the text of the two system prompts. Everything else is identical to v5: input corpus
(artifact 12591716174, titles and summaries), model (`anthropic/claude-sonnet-5.5` via OpenRouter,
`json_object`, `max_tokens` 6500 for extraction), validator `ingestion/ubik_v5_extraction_validator.py`,
retrieval (`intfloat/multilingual-e5-small`, top 5 per event, soft nature filter, cross-source only,
same deduplication), cautious grouping, `resolve_part_of`, `compose_connected_v5`.

Frozen prompts (commit `0ccbdc202a1e2fcec94e54fc1af4d3af068df750`), read verbatim from file and
hash-checked by `ingestion/ubik_v51_prompts.py` before every paid call:

| File | SHA-256 |
| --- | --- |
| `prompts/v5.1/extraction.txt` | `22a63958b94064356077432f080c49fa5f15834fa8597e76154c67fde106290a` |
| `prompts/v5.1/pair_judge.txt` | `703e308ae07b5e1c500674b6238dbe0248a5cdef0598921cd7beb8a5299d686f` |

Reason for v5.1: the v5 prompts (and the v4 hybrid judge, the v2 extractor and the monarch pilot)
contained hints derived from the evaluation sample, one with a factual error. Historical baselines are
kept untouched and are declared contaminated, not independent.

## 2. Order of stages, with stop points

1. **Extraction only** (`ukraine-v51-extraction.yml`). Ceiling: 0.30 USD. Every raw response is saved
   before validation. No retrieval, no judge.
2. **Blind mapping** of v5.1 events to the frozen reference (section 4), frozen with SHA-256 and
   committed before stage 3.
3. **Candidate pairs**: generated with the v5 retrieval from the v5.1 extraction, saved with
   similarities, parameters and hash, committed before any judgment.
4. **Judges** on the same frozen pairs, prompt `pair_judge.txt`, no reference and no mapping in input:
   Sonnet 5.5 (`json_object`, ceiling 1.00 USD) and DeepSeek V4.1 Flash
   (`deepseek/deepseek-v4.1-flash-1017`, Nebius FP8, no fallbacks, reasoning disabled, strict JSON
   schema, ceiling 0.10 USD). The response-format difference is a declared technical variable.
   Invalid responses: one retry with identical request; after two invalid responses the pair is
   `uncertain` with `invalid_after_retry`; 7 or more on 131-like totals (5%) makes the arm partial.
   Results of the two judges are compared only after both are complete.
5. **Evaluation** with the weights of "Ubik — Riferimenti di valutazione" (column "differenza persa"),
   split vicende counted once per reference vicenda, blockers first.

Ukraine is diagnostic. Promotion of any judge is decided on the AI corpus with the common criterion of
2026-10-28 08:20 (tolerance T measured from two Sonnet runs). The monarch pilot is rerun with the
same v5.1 contract only after its harmonisation; it does not block Ukraine.

## 3. Predictions (registered 2026-10-28 09:45, before the prompts were final)

Each prediction is compared with v5 of the same judge; a falsified prediction is declared, not
reinterpreted.

| N. | Prediction | Confirmed if | Confidence |
| --- | --- | --- | --- |
| 1 | No merge between the diesel deal (A) and the executive order (B) | Zero A/B pairs in one group, for each judge | Medium |
| 2 | More uncertain A/B pairs than in v5 | Count of uncertain A/B pairs grows vs v5, for each judge | Medium |
| 3 | The diesel-deal vicenda is less fragmented | Fewer than the four fragments of v5 with Sonnet | Medium |
| 4 | The two reactions recorded as mentions are recovered | n14 reacts_to the ceasefire; n27 reacts_to the refinery strikes | Medium |
| 5 | The non-existent EU agreement disappears | No reason attributes the diesel deal to the EU | High |
| 6 | Without hints DeepSeek loses more than Sonnet on the A/B trap | DeepSeek has more uncertain or merged A/B pairs than Sonnet | Low |
| 7 | Cost changes little | Extraction and judgment within ±20% of v5, same model | Medium |

Prediction 1 is a blocker: a judge that merges A and B does not go on to the AI corpus.

## 4. Blind mapping procedure

Blind to v5.1 judgments, not to sources: the mapper reads the evidence of every event and reference item.

1. Inputs frozen: source ids, supplied texts, existing reference, code commit, prompt hashes.
2. Extraction only; nothing else runs.
3. Each v5.1 event is matched to reference items by actor, action, object, time, actuality and
   evidence. One-to-many and many-to-one matches are allowed when extraction split or merged content.
4. Anomalies are recorded, not forced: missing reference items, unmatched events, events too vague
   to match, uncertain matches.
5. The mapping table (`extracted_event_id`, `reference_id`, `match_status`, `evidence`, `rationale`,
   `reviewer`) is frozen with SHA-256 and committed. It is not changed in light of verdicts.
6. Pairs are generated and frozen (stage 3), then the judges run without reference or mapping.
7. Any later correction of the mapping is justified and reported separately; the preregistered
   result is never rewritten.

Roles: Claude prepares the mapping; an independent reviewer agent, started without this
conversation and without any judgment, checks it against sources and reference before freezing.
Disagreements are shown to the project owner. Knowledge of old v5 judgments by Claude is declared as
a limitation, not treated as a breach of blindness.

## 5. Declared limitations

- The generic definitions in the v5.1 prompts were developed while working on Ukraine; v5.1 on
  Ukraine shows how much results depended on the hints, it is not an independent validation.
- One rule is explicitly sample-derived: "an instance of a broad/generic category is not part_of"
  (from the DeepSeek V4.1 Flash relation S188:e1 -> S408:e7, a pair excluded from scoring).
- Post-hoc checks not enforced by the validator are reported, never used to reject or repair:
  duplicate `news_key`, null `primary_event_id` without `context_only`, an event in both
  `reacts_to` and `mentions`.
