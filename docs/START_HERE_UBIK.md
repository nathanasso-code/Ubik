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
