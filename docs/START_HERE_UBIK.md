# UBIK — START HERE (2026-10-11)

Working branch: develop/ubik-core. This is the continuity note for future chats.

## Open the working preview
GitHub Actions run: https://github.com/nathanasso-code/Ubik/actions/runs/38120499732
After the run completes, open its artifact named ai-models-discovery and download UBIK_PREVIEW.html. This static HTML displays actual feed items, source counts, links, and acquisition errors. Artifacts expire after 14 days.

## Verified baseline
Previous completed live run: https://github.com/nathanasso-code/Ubik/actions/runs/38089481756
32 pilot registry entries; 24 enabled RSS feeds; 19 successful requests; 17 feeds returned items; 2 arXiv feeds returned zero raw items; 5 failed. 2,638 raw entries from successful feeds and 2,638 normalized observations. 12 additional Italian candidate sources remain disabled. Total catalog entries: 44. These are not 44 successfully acquired sources.

Five unresolved RSS issues: HTTP 403 on the-batch, jack-clark, economics-of-ai, frankly-counterfactual; 3 MB size cap on dan-luu. Do not bypass access restrictions. arxiv-cs-ai and arxiv-cs-cl had zero upstream items in the measured run.

## Key files
- scripts/discover_ai_sources.py: RSS acquisition
- ingestion/preview_html.py: standalone browser preview
- ingestion/coverage_cli.py: inventory and acquisition quality
- ingestion/cross_topic_inventory.py: 44 catalog entries, candidates kept separate
- ingestion/feed_triage.py: failure classification
- ingestion/source_quality.py: freshness and duplicate diagnostics
- .github/workflows/ai-discovery-pilot.yml: collection and artifact packaging
- docs/GITHUB_DEVELOPMENT_AND_SOURCE_AUDIT_2026-10-10.md: previous work
- docs/RSS_SOURCE_VERIFICATION_2026-10-10.md: live RSS results
- docs/SOURCE_EXPANSION_AND_TRIAGE_2026-10-11.md: source diagnostics

## Product constraint
Ubik uses matrix topics with tag clouds, then sources, cards and optional epistemic nuclei. Do not restore Press, Insights or Pulse. Acquisition is independent of editorial selection. Do not start editorial phase 4 yet.

## Three next actions only
1. Verify latest workflow run success and presence of UBIK_PREVIEW.html artifact, then review source-by-source counts.
2. Investigate five RSS failures via documented public endpoints without bypassing access restrictions. If unavailable, keep explicit failure states.
3. Expand practical non-AI source coverage in small verified batches, and test existing HN/GDELT connectors with bounded public requests. Keep the same pipeline; do not start new frameworks.

SQLite is a local experiment; PostgreSQL is not deployed. No production deploy or recurring collection job has been enabled by this work. Check CI after each change. Do not modify main.

## 2026-10-11 next increment: general-world pilot
Four enabled RSS feed candidates were added to the SAME registry and SAME workflow: BBC World, The Guardian World, Al Jazeera English and NYT World. arXiv category feed URLs were switched to the officially documented rss.arxiv.org host. The pilot now has 36 registry entries, 28 enabled RSS feeds, and the cross-topic inventory has 48 entries including the 12 disabled Italian candidates. These are configuration counts, NOT verified success or material totals. Check the latest AI sources discovery pilot run before claiming results. The five earlier RSS errors remain unresolved unless a newer run proves otherwise. Do not create additional branches or change editorial selection.

## VERIFIED 2026-10-11 — general-world live collection
Successful run: https://github.com/nathanasso-code/Ubik/actions/runs/38120774636 ; CI success: https://github.com/nathanasso-code/Ubik/actions/runs/38120774716 . **2,797 raw and normalized RSS observations**, **23/28 successful feeds**, **21 with material**, **2 arXiv feeds returned zero**, **5 failures unchanged**. Four new feeds ALL worked: BBC World **32**, Guardian World **45**, Al Jazeera English **25**, NYT World **57**; total **159 new observations** relative to the earlier 2,638-observation pilot. The run created `UBIK_PREVIEW.html` in its artifact. These are not necessarily unique articles, and not daily throughput.

## Preview usability fix
`ingestion/preview_html.py` now uses **presentation-only round-robin sampling** of article cards so OpenAI/Hugging Face do not crowd out BBC/Guardian/Al Jazeera/NYT. Raw and normalized archives remain unchanged, and there is no editorial ranking. Tests: `tests/test_ingestion_preview_html.py`. Confirm the next preview workflow run before claiming the changed artifact is available. The 5 failed feeds and arXiv empty feeds remain visible in diagnostics; fix them only where legally and technically feasible, without blocking the demo.

## 2026-10-11 — first topic selection pilot
See `docs/AI_TOPIC_SELECTION_PILOT_2026-10-11.md`. A review-only, metadata-only selection module `ingestion/topic_feed_pilot.py` now produces `ai-topic-feed-review.json` in the EXISTING RSS workflow artifact: maximum 30 AI-related candidates, source-balanced, within 14 days where dates exist, distinct URLs preserved as standalone. Topic: “Modelli e sistemi di intelligenza artificiale”; matrix “Intelligenza artificiale”; overlapping areas and tags. This is NOT semantic extraction, same-event card clustering, trend detection, credibility scoring or automatic publication. These require evaluation and separate future implementation. Tests: `tests/test_ingestion_topic_feed_pilot.py`. Verify GitHub Actions success and real candidate counts before asserting operational coverage. Historical contract: same event differs from same topic; nucleus is a persistent issue, not an event cluster. Keep existing branch and no new infrastructure.

## 2026-10-11 — AI topic feed reviewed against live pilot
Verified live discovery run https://github.com/nathanasso-code/Ubik/actions/runs/38122041106 : **2,857** collected observations; review-only selector found **106** topic candidates and exposed **30**. The report generation and artifact upload succeeded; no automatic publication or validated event merges. Source-balanced topic review HTML `UBIK_TOPIC_AI_REVIEW.html` is now generated alongside `ai-topic-feed-review.json` by `ingestion/topic_feed_preview.py`; check the NEXT live workflow artifact for this new file before asserting it is present. The older `UBIK_PREVIEW.html` is the full raw-material view. Selection logic still relies on keywords, 14-day recency and per-source balancing. Next work: manually inspect actual 30 entries, label topical relevance, same-event candidate pairs, independent origins, and valuable singletons; then calibrate semantic extraction. Never claim a trending or credibility score from this pilot.

## 2026-10-11 — 30 real item audit and event-matching fix
Live run https://github.com/nathanasso-code/Ubik/actions/runs/38122381477 passed: 105 AI topic candidates, 30 visible, zero provisional cross-source pairs from the **30-only** title matcher. Concrete examples and caveats are in `docs/AI_TOPIC_30_REAL_ITEMS_AUDIT_2026-10-11.md`. The report now includes `all_candidates`; `ingestion/topic_event_review.py` compares the entire candidate pool **before** the 30-visible feed cap. This is a candidate retrieval fix, not semantic event validation or automatic card publication. Tests: `tests/test_ingestion_topic_event_review.py`. Verify the next live run for actual full-pool pair counts. Prioritize reviewing title false positives and primary-source independence; don't infer newsworthiness or trends from one RSS snapshot.

## 2026-10-11 — Extractive topic message evidence
Verified full-pool event comparison live run https://github.com/nathanasso-code/Ubik/actions/runs/38122519470 : 105 candidate documents, 30 visible, **1 title-overlap candidate pair**, **0 automatic merges**. Implemented `ingestion/topic_evidence.py` and `tests/test_ingestion_topic_evidence.py`; the next RSS workflow produces `ai-topic-evidence-review.json` across ALL topic candidates, with verbatim attributed source-description sentences, explicit title-only status when summaries are missing, weak content-type hints, and no claim verification or publication. This is **not** LLM semantic extraction, full-text retrieval, or automatic epistemic grouping. The arXiv Atom API officially provides abstracts in the `summary` element; those are already collected as feed descriptions. Review real extraction coverage in the next live run before claiming usefulness. Next stage should measure errors and annotate real pairs before adding selective paid semantic processing.

## 2026-10-11 — live evidence coverage and uncertainty review
Live workflow https://github.com/nathanasso-code/Ubik/actions/runs/38122615761 **success**: 105 candidate documents, 30 visible, **100 with extractive description evidence**, **5 title-only**, one unverified title-overlap event pair, zero merges. Added `ingestion/topic_review_priority.py` + `tests/test_ingestion_topic_review_priority.py`, generating `ai-topic-priority-review.json` in next workflow artifact. It sorts full-pool review by explicit evidence gaps and potential same-event pairs, **not by newsworthiness or publisher credibility**. All decisions remain unreviewed; no automatic publication. Validate real counts in next live run. Next work: evidence-grounded reviewer judgments of topic relevance, source-message, origin independence, importance, and exact event identity; only then calibrated low-cost semantic assistance.

## 2026-10-11 — Real review queue and 30-document editorial worksheet
Verified live workflow https://github.com/nathanasso-code/Ubik/actions/runs/38122792406 success: **106** AI candidates, **100** with substantive feed-description evidence, **6** title-only, **1** unverified event candidate pair, zero automatic merges. Review reason counts: **2** involved in candidate pair, **6** missing substantive descriptions, **29** without specific area, **71** routine content review. Implemented `ingestion/topic_editorial_worksheet.py` and tests; the next workflow exports `ai-topic-editorial-worksheet.csv` with a **stratified, source-balanced sample of up to 30**, including verbatim evidence and BLANK human editorial fields. This is not AI-generated central message extraction or completed human annotation; it is the first reproducible evaluation sheet. Do not publish or score importance until those fields are independently reviewed. Sample selection deliberately includes uncertainty cases rather than mirroring the 30 visible feed items.
