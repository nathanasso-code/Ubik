# Ubik — Pilot decision: AI topic feed selection (2026-10-11)

## Recovered product contract

Source/document, same-event cluster, epistemic card, persistent nucleus, debate and validation are distinct. A matrix topic has thematic areas and a tag cloud. The example “Guerra russo-ucraina” → “Attacchi all'Ucraina” is topic specialization, not an event merge. A card groups the same bounded event, not all documents on a common subject. Nuclei follow persistent questions across cards. Preserve authors, publishers, links and acquisition channels; source syndication is not independent evidence. Do not revive Pulse/Press/Insights.

## First scoped pilot

Topic: **Modelli e sistemi di intelligenza artificiale**, matrix **Intelligenza artificiale**. Initial overlapping areas: capabilities, research/evaluation, releases/products, safety/governance, economic/social impact. These are navigation labels, not a requirement to split tightly linked AI news into separate topics.

`ingestion/topic_feed_pilot.py` is a **review-only**, zero-LLM-cost metadata baseline. It takes the existing `ai-models.json` acquisition output, detects explicit AI terms in title and feed summary, deduplicates identical URLs, excludes dated material older than 14 days, and exposes up to **30** candidates in a source-balanced sample. Missing dates remain eligible but sort last. Every distinct URL remains a singleton; no automatic same-event merges, epistemic validation, nucleus publication or UI deployment. The full raw archive remains available. Its review JSON is written into the existing workflow artifact as `ai-topic-feed-review.json`.

## Proposed next implementation stages, not yet validated

1. **Low-cost topic attribution**: exact rules and cheap lexical/embedding retrieval first; uncertain items abstain. Do not treat the registry's pilot topic label as ground truth. Assign multiple area tags if justified. Evaluate with human-reviewed positives, hard negatives and cross-lingual examples.
2. **Extract source message**: for each source record a concise, attributed central claim/event, date, actor, scope and evidence span. Feed metadata supports only a provisional hypothesis. Where lawful full text is accessible, use selective AI extraction with cache and per-document token budget; never invent evidence or conflate original publisher and commentator.
3. **Event clustering**: generate candidates with time, entities, URLs and text similarity; merge distinct URLs only after event identity is supported, initially by review. Same topic alone never sufficient. Keep singleton sources. Deduplicate syndication and record source-dependency lineage.
4. **Trend and credibility**: use repeated acquisition snapshots, growth in *independent* origins, time decay and cross-channel corroboration, not raw volume alone. Source credibility is topic-dependent and evidence-based; small expert blogs and primary scientific sources must remain eligible. An important singleton can be surfaced even with low trend.
5. **Feed budget**: start with 30 visible entries; monitor redundant cards, unique high-value singletons, topic coverage, false merges and missed developments. Separate “not displayed in feed” from “not acquired”; keep all original sources searchable.

## Honest limits

The baseline is NOT a semantic classifier, trend detector, full-text interest evaluator, automatic card clusterer or publication-ready feed. It is intentionally a testable first review queue. Dates and feed descriptions can be absent or misleading. Real trend requires time-series snapshots, which the current one-off RSS run does not provide.

## Next verification

Run CI and real `AI sources discovery pilot` workflow, confirm `ai-topic-feed-review.json` exists and inspect its candidate counts. Review 30 candidates manually before calibrating selection or authorizing publication. Continue on `develop/ubik-core` only. Keep `docs/START_HERE_UBIK.md` as the continuity entry point.
