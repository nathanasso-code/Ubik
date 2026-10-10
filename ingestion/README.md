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
