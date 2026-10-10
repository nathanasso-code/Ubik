# Federated discovery pilot — acquisition before editorial selection

## Scope
The acquisition stage gathers all eligible observations from configured sources.
It does not rank, suppress, cluster, summarize or validate news stories.

## Implemented
- Existing RSS source registry and discovery pilot (32 configured sources at last inspection).
- `scripts/discover_hacker_news.py`: public Hacker News `newstories` metadata connector, explicitly opt-in (`--live`), default 30 requests, bounded to 500, per-request pause and isolated failures. Links to original articles are discovery signals, not extracted article content.
- `scripts/merge_discovery_observations.py`: URL-based document hints and preserved observations across connectors. Does not equate a shared URL with independent corroboration.
- `scripts/build_event_anchor_review.py` remains a *diagnostic* review aid, not the feed acquisition filter. It must never restrict the incoming corpus.

## Local commands
```sh
python scripts/discover_hacker_news.py --live --limit 30 --output data/discovery/hacker-news.json
python scripts/merge_discovery_observations.py data/discovery/ai-models.json data/discovery/hacker-news.json --output data/discovery/federated.json
python -m unittest discover -s tests
```

## Operational safeguards
- No credentials, paywall bypass or unauthorised crawling.
- Metadata only. Verify individual provider conditions and personal-data retention before production.
- Respect 429 responses, backoff and source-level budgets before scheduling high-volume runs.
- Archive snapshots with run timestamps and provenance; document time coverage and sampling bias.
- Do not infer publisher independence from different discovery paths.
- Canonical URLs are only *hints*: redirects, syndication and URL aliases require later reconciliation.
- Keep raw observations for audit; deduplication must not erase acquisition history.

## Next connector candidates
1. GDELT DOC public article-list API for *discovery*, with documented query coverage and provider limits. Avoid interpreting keyword queries as comprehensive news coverage.
2. AT Protocol/Bluesky public discovery and streaming where allowed; store post IDs and references, handle deletions.
3. OpenAlex/arXiv metadata with license-aware document handling.
4. Direct RSS/Atom autodiscovery and sitemap coverage expansion.

## Evaluation before ranking
Report daily observation counts, distinct URL hints, source mix, geographic and language coverage, error rates, duplicates, freshness, ingestion costs and estimated missed coverage. Do not manually preselect event families to determine which articles enter the experiment.
