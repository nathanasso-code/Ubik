# Topic feed quality and autonomous source catalogue (draft v1)

## Compatibility
The new tables are additive and do not modify the existing event corpus or Vercel Blob question feed. Do not deploy the SQL without checking existing production schema and permissions. No background fetch or production write is implemented.

## Ingestion
RSS, GDELT, Hacker News, scientific APIs, Mastodon and Bluesky are **discovery channels**. Normalize candidate URLs, resolve publisher/canonical identity safely, and preserve every observation in `ubik_document_discoveries`. URL equality is a preliminary identity hint, not proof of same article. Domain is not proof of publisher identity. Resolve redirects only with allowlisted HTTPS destinations, SSRF protection, rate limits and provider policy checks.

## Registry
`ubik_publishers` holds independently monitorable domains and their official feeds. Social discoveries seed this registry, but future updates come directly from eligible RSS/API endpoints. Do not treat discovered third-party URLs as authorization to scrape copyrighted full text.

## Topic membership
`ubik_topic_documents` holds topic-specific editorial status, rather than storing three copies of each document. **Esplora** is all nonexcluded candidates; **Rilevanti** is relevance-reviewed or has transparent qualifying attention evidence; **Essenziali** requires documented review and explicit approval. An essential source must be relevant. Revocations and reasons must be appended to review history transactionally by the eventual application service.

## Ranking and integrity
Social signals increase review priority; they do not assert factual validity. Multiple accounts must be independently assessed; follower count, linked domain verification and substantive discussion are distinct signals. Missing signals remain unknown, never zero. Essential retention is editorially managed, not an automatic recency threshold.

## Implementation boundary
`ingestion/social_source_catalog.py` and `ingestion/topic_quality_views.py` are offline prototypes. The migration is a proposed persistence contract. Next: run unit tests in CI, reconcile existing source catalogue, build safe discovery-to-publisher normalization and a read-only topic API. Production UI remains unchanged.
