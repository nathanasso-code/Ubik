# Blind epistemic discovery — evaluation protocol (13 October 2026)

## Research question

Can an unseeded, multi-source scan identify **unexpected, source-grounded relationships** relevant to existing controversial Ubik topics, including links that a topic-keyword search would miss?

**Important:** the previously discussed datacenter case is a **held-out retrospective probe**. It must not enter discovery queries, stopword/boost lists, prompt examples, candidate scoring or manual selection until the blind candidate list has been frozen.

## Stage 1: blind discovery (implemented)

`ingestion/blind_relation_hypotheses.py` processes the existing global RSS snapshot, without topic queries or datacenter terms. It emits pairs of terms that co-occur in titles of at least two documents on different publisher hosts, with linked titles and URLs. This is only a weak lexical baseline. It does **not** infer causation, corroboration, disagreement, or event identity. Output: `data/discovery/blind-relations-review.json` in the global pilot artifact.

## Stage 2: deep semantic retrieval (partially implemented)

`ingestion/semantic_topic_router.py` supplies an optional multilingual E5 encoder for hashtag contexts and a **fixed catalog** of topics. The live-model workflow is defined but its successful execution and thresholds have not yet been established. The current social expansion is a small query-driven sample, not a broad social archive. Do not claim the E5 router has found an epistemic relationship.

Needed next: multilingual embedding search across **all observed document titles, descriptions, and shared-link contexts**, not only hashtag groups. Persist a ranked candidate neighborhood for every document, including cross-language matches and dissimilar wording; retain original evidence and timestamps. Do not equate embedding similarity with causal relation.

## Stage 3: adjudicate relation *types*

For each frozen candidate, require the reviewer to label:
- `same_event` — independently assessed shared real-world occurrence;
- `support` or `contradiction` — only when *explicit claims* are extracted and compared against source passages;
- `context` — same subject, distinct event;
- `potential_causal_link` — source **asserts** a causal relationship, not model inference;
- `spurious` or `insufficient_evidence`.

Capture exact supporting passages, document URLs, dates, original publisher, repost genealogy, reviewer and reason. Contradiction must compare propositions, not positive/negative sentiment.

## Stage 4: held-out retrospective datacenter probe

Only **after** blind candidate generation is frozen, search the candidate inventory for the previously known case, and inspect whether a relevant signal was present. Report detection / miss, ranking, supporting evidence, and whether detection was possible from the sampled source coverage. A miss is a valid scientific result. Do not secretly add datacenter keywords to discovery.

## Evaluation and promotion gates

Track top-k precision of useful relationships, coverage/recall against manually reviewed random documents, source-origin diversity, temporal coherence, multilingual quality, and abstention. Compare global-first vs topic-led under the same source/time budget. No new topic or hashtag section is automatically created. No public epistemic card is published until reviewed. Keep the original pilot outputs and failures reproducible.
