# Ingestion subsystem boundary

`ingestion/` is the independent, provider-facing **acquisition** module.

## Dependency direction
```
External provider -> ingestion adapters -> observations -> durable storage
                                                   |
                                            later consumers
                                  (dedup / selection / clustering / UI)
```
Ingestion must never import ranking, editorial selection, cluster evaluation, UI or LLM modules. Consumers may import `ingestion.contracts`; providers may be replaced without changing consumer semantics.

## Contract
`observation()` emits URL, title, provider/source IDs, discovery endpoint, raw provider date, metadata and explicit `not_assessed` editorial/event flags. `canonical_url_hint` removes known tracking parameters but does not claim canonical document identity. Keep raw observations separately from deduplicated document hints.

## Implemented adapters
- `ingestion/gdelt_doc.py`: public GDELT DOC ArtList discovery. Queries are **scoped**, not a comprehensive news firehose. Maximum 250 records per query and a `potentially_truncated` indicator. GDELT `seendate` is not assumed to be publication time.
- Existing RSS and Hacker News scripts remain independent legacy/pilot connectors; gradual migration to this contract can happen without disrupting their workflows.

## Local dry-run / live
```sh
python -m ingestion.discover_gdelt --query 'climate change' --timespan 1h
python -m ingestion.discover_gdelt --query 'climate change' --timespan 1h --maxrecords 75 --live
python -m unittest discover -s tests
```

The live call is explicitly opt-in. No scheduled ingestion, Supabase writes, production deployment, API credentials, article-body extraction or editorial filtering is introduced here.

## Operational roadmap
1. Implement per-source budgets, conditional HTTP requests, retry/backoff, run manifests and metrics.
2. Move RSS and HN adapters behind the same observation contract.
3. Add consent/terms-aware AT Protocol and scientific metadata adapters.
4. Store immutable acquisition observations and source policy records in a dedicated schema before exposing data to selection/clustering.
5. Evaluate completeness, freshness, duplicate ratio, language/source distribution and cost from unselected rolling acquisition windows.

## Important limitation
GDELT DOC search terms impose selection bias. Use it as *supplementary discovery* alongside direct feeds and, where feasible and permitted, broader public export streams. Do not treat query hits as the universe of eligible news.

## Offline federation and budgets

`ingestion/legacy_adapters.py` maps existing RSS and Hacker News snapshots to the shared contract without changing the legacy fetchers. `ingestion/federate.py` merges offline snapshots and reports counts of raw observations, URL hints, source pairs and errors; it **does not** select or cluster stories.

```sh
python -m ingestion.federate data/discovery/ai-models.json data/discovery/hacker-news.json --output data/discovery/federated-ingestion.json
```

`ingestion/budgets.py` defines per-source request and observation accounting. This is a reusable primitive, **not yet wired into the network fetchers**. Until integrated, live adapters rely on their own explicit bounded parameters. Never treat the existence of a budget class as proof of enforced rate limiting in production.

## Social and scientific connectors (opt-in, not scheduled)

`ingestion/public_adapters.py` provides independent, metadata-limited adapters for:

- **Bluesky**: public AppView `getAuthorFeed`, bounded to 100 posts per request, actor-specific; retains post URL/AT URI, author DID and a short preview. This is *not* a firehose. Deletion/privacy lifecycle handling is required before continuous archival.
- **Mastodon**: public **local** timeline for an explicitly named instance, bounded to 40 statuses; ignores nonpublic statuses and boosts; stores a post reference rather than the status HTML body. Some instances disable unauthenticated access; instance rules must be respected. Do not use user-supplied instance URLs without network egress/SSRF controls.
- **OpenAlex**: publication-date-bounded works metadata, max 100 records/page, with a cursor for further pages. API access, rate limits, and any API-key requirements must be confirmed at deployment. This is not full-text extraction.

Examples (all offline validation unless `--live` is supplied):
```sh
python -m ingestion.discover_public --live bluesky --actor example.bsky.social --limit 30
python -m ingestion.discover_public --live mastodon --instance mastodon.social --limit 20
python -m ingestion.discover_public --live openalex --from-date 2026-10-09 --to-date 2026-10-10 --per-page 50
```

Each connector makes one bounded API call per invocation, not an automatic pagination loop. Output is a replaceable snapshot: use distinct filenames for repeated runs until durable append-only storage is implemented. `ingestion.federate` accepts these snapshots alongside RSS, HN and GDELT. These adapters are not yet scheduled, benchmarked against live endpoints or configured for production.

References:
- https://docs.bsky.app/docs/api/app-bsky-feed-get-author-feed
- https://docs.joinmastodon.org/methods/timelines/
- https://help.openalex.org/api/filtering/
- https://help.openalex.org/api/paging/
