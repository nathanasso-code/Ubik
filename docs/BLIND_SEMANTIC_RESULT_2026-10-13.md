# Blind semantic pilot — frozen-run retrospective audit

**Frozen input:** GitHub Actions run [38320346965](https://github.com/nathanasso-code/Ubik/actions/runs/38320346965), commit `42a358656f86daca6fa9d203360110199ab21dfe`, artifact `semantic-topic-review`, file `blind-semantic-neighbors.json`. This evaluation was written **after** the output was frozen; the benchmark terms were not fed to the retrieval stage.

## Observed result

- 324 publisher RSS document hints, **1,258** cross-host semantic neighbor pairs at cosine ≥ 0.72. Scores are not probabilities; cross-host does not imply independent evidence.
- **Held-out datacenter signal was recovered in rank 59 of 1,258 pairs (cosine 0.8815)**:
  - BBC RSS title: [Ukraine strikes Yandex data centre in third attack on Russian tech giant](https://www.bbc.co.uk/news/articles/cw0k0g57mk3zo?at_medium=RSS&at_campaign=rss)
  - Ars Technica RSS title: [Ukraine’s drones knock out AI data center belonging to “Russia’s Google”](https://arstechnica.com/gadgets/2026/10/ukraines-drones-knock-out-ai-data-center-belonging-to-russias-google/)
- A second link at **rank 63 (cosine 0.8791)** associates the BBC title with [Russia was not ready for the data center war it started with Ukraine](https://arstechnica.com/gadgets/2026/10/russia-was-not-ready-for-the-data-center-war-it-started-with-ukraine/), also from Ars Technica.
- These links did **not** require the exact term `Yandex` to be shared: the BBC title uses Yandex; the first Ars Technica title describes “Russia’s Google.” The titles do share `Ukraine`, `data centre/center`, and `strikes/drones` conceptually, so this is **not proof of deep non-obvious reasoning**. It is, however, a concrete blind cross-publisher candidate recovered through embeddings, more specific than the earlier `russia/ukraine` lexical edge.

## Negative examples in the same frozen ranking

- **Rank 142, cosine 0.8539**: Russia/Ukraine datacenter war vs [local backlash to a datacenter in an American city](https://www.theguardian.com/us-news/2026/oct/09/datacenter-backlash-ibm-east-fishkill-new-york). Shared infrastructure term, **unrelated issue**; a dangerous false positive if treated as one event.
- **Rank 159, cosine 0.8515**: reported Russian strikes on Ukrainian energy sites vs reported Ukrainian strike on Russian AI datacenter. **Related strategic context, opposite direction of action, not the same event**.
- **Rank 58, cosine 0.8818**: reported Ukrainian drone-related airport disruption vs reported Ukrainian strike on a data center. **Same broad conflict, distinct targets**, not necessarily same event.
- Multiple top-ranked near-identical titles are duplicates of a possible news event; these are useful for clustering but do not demonstrate new epistemic relationships.

## What this proves — and does not

The pipeline can surface the **previously held-out datacenter case without topic or case-specific search terms** in a limited publisher corpus, and can join non-identical cross-publisher headlines. It **does not** establish that the underlying reports are factually true, that the sources independently confirmed an event, that one caused another, or that Ubik has detected contradictions/support among propositions. All titles are attributed to RSS observations and were not independently checked against full article bodies.

## Required next gate

1. Extract full source passages and explicit claims with URLs, dates, agent/action/target, and source provenance.
2. Label `same_event`, `related_distinct_events`, `context_only`, `contradiction`, `support`, `insufficient_evidence` using **source text**, not embeddings.
3. Test on a representative randomly selected set, not only datacenter examples; measure top-k precision, false merges and missed cross-language pairs.
4. Only reviewed, source-grounded links can appear as epistemic edges in topic cards. No new hashtag sections or topic creation.
