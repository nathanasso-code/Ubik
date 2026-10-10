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
- **Crossref**: date-bounded bibliographic metadata, cursor-based pagination; does not fetch copyrighted full texts.\n- **OpenAlex**: publication-date-bounded works metadata, max 100 records/page, with a cursor for further pages. API access, rate limits, and any API-key requirements must be confirmed at deployment. This is not full-text extraction.

Examples (all offline validation unless `--live` is supplied):
```sh
python -m ingestion.discover_public --live bluesky --actor example.bsky.social --limit 30
python -m ingestion.discover_public --live mastodon --instance mastodon.social --limit 20
python -m ingestion.discover_public --live openalex --from-date 2026-10-09 --to-date 2026-10-10 --per-page 50\npython -m ingestion.discover_public --live crossref --from-date 2026-10-09 --to-date 2026-10-10 --rows 50
```

Each connector makes one bounded API call per invocation, not an automatic pagination loop. Output is a replaceable snapshot: use distinct filenames for repeated runs until durable append-only storage is implemented. `ingestion.federate` accepts these snapshots alongside RSS, HN and GDELT. These adapters are not yet scheduled, benchmarked against live endpoints or configured for production.

References:
- https://docs.bsky.app/docs/api/app-bsky-feed-get-author-feed
- https://docs.joinmastodon.org/methods/timelines/
- https://help.openalex.org/api/filtering/
- https://help.openalex.org/api/paging/
\n- https://api.crossref.org/swagger-ui/index.html\n
## Reliability and archive increment

- `transport.py` provides a shared JSON transport with bounded response size, timeout and at most three attempts by default. Retries are limited to transient HTTP 429/5xx and network errors; `Retry-After` is capped at 30 seconds. It is now used by the Bluesky, Mastodon, OpenAlex and Crossref adapters.
- `archive.py` provides an immutable, timestamped, SHA256-addressed local snapshot archive. An existing snapshot cannot be overwritten.
- `discover_public.py --archive-dir data/discovery/runs` uses append-only archival mode instead of overwriting a single JSON file. Files are local to the runner and **not persistent across ephemeral CI runs** unless explicitly uploaded to approved storage.
- `budgets.py` remains a standalone budget primitive; a fully integrated multi-provider scheduler, persistent cursor/checkpoint store and production-grade request budgets are **not yet implemented**.
- The Mastodon adapter rejects obvious localhost/private hostname and IP-address targets, but this is **not complete DNS rebinding or redirect SSRF protection**. In production, use a configured instance allowlist and restricted egress.

No recurring job is enabled. Do not interpret offline tests as a live API benchmark.

## Resumable bounded batch runner

`python -m ingestion.run_batch` is a **manual, explicitly opt-in** batch runner for Bluesky, Mastodon, OpenAlex and Crossref. It supports at most 20 pages of at most 20 records each, with at least 0.5 seconds between pages. The per-run `SourceBudget` is enforced before each request and after each response. The runner archives each successful page, then atomically updates a source/scope-specific checkpoint with its cursor and archive digest.

```sh
python -m ingestion.run_batch bluesky --source example.bsky.social --max-pages 2
python -m ingestion.run_batch bluesky --source example.bsky.social --max-pages 2 --live
python -m ingestion.run_batch openalex --source openalex-works --from-date 2026-10-09 --to-date 2026-10-10 --live
```

Social feeds start a fresh polling cycle after reaching the end; scientific date windows are marked complete. Source scope and date range form the checkpoint identity. This is **at-least-once** acquisition, not exactly-once: overlapping social pages and crash retries may generate duplicate observations; downstream URL and stable external-ID deduplication must preserve their separate provenance.

**Limitations:** POSIX single-filesystem locking only in file mode; no cloud checkpoint persistence, no scheduled live execution, no provider-specific quota accounting, no deletion reconciliation, and no proof of real API coverage. Do not run concurrent batches for the same source/scope; a database lease and durable object store are required before unattended distributed execution. No live network requests are made without `--live`.

## Offline coverage and overlap audits

`ingestion.audit` measures raw observation counts by connector and source, distinct URL hints, repeated source IDs, overlapping URL hints across sources/connectors, and timestamp buckets. The timestamp buckets are descriptive only: GDELT seen dates, provider-created dates and scholarly publication dates are **not equivalent clocks**. Overlap does not establish independent corroboration.

```sh
python -m ingestion.audit_archive data/discovery/runs --output data/discovery/coverage-report.json
```

The archive auditor federates each archived snapshot without filtering by event, source quality, topic or editorial importance. It reports invalid files and federation errors separately. The archive must already exist; this command does not perform network calls. It does not compute sampling completeness or population recall, which require an independently defined reference universe.

## Heterogeneous experimental run

`ingestion.experiment_plan` validates a source list with strict per-source limits (at most 24 sources, 10 pages each, 20 observations/page). `ingestion.experiment` runs sources independently, reports failures by source, and audits the resulting archived observations. **Dry-run is the default**.

```sh
python -m ingestion.experiment config/ingestion-experiment.example.json
# Only after reviewing source scope, rights, instance rules and egress policy:
python -m ingestion.experiment config/ingestion-experiment.example.json --live
```

The example source list is illustrative, not a coverage benchmark. In particular, a Bluesky actor feed is not the entire Bluesky firehose, and a Mastodon local timeline is not the fediverse. The experiment runner does not claim representative sampling, comprehensive coverage, editorial quality, or cross-provider independent verification.

The live mode remains **manual and untested against actual provider responses**; no scheduled workflow or production database writes are enabled. Source archives and checkpoints are local and need external persistence before use on ephemeral runners.

## Live smoke-test readiness (not executed)

`.github/workflows/ingestion-live-smoke.yml` defines a **manual-only** GitHub Actions smoke test for one public provider page, at most five metadata observations, with read-only repository permissions and a temporary archive deleted at job exit. It does not print individual social posts. GitHub normally requires a `workflow_dispatch` workflow to exist on the repository's **default branch** before it can be triggered from the Actions UI; this branch-only workflow is therefore a preparation artifact, **not an already runnable live test**. No changes to `main` were made.

The development environment used for this change cannot resolve public API hosts, so no successful live request has been observed. Before enabling manual dispatch, review source permissions and provider policies, promote the workflow through the normal review process, and verify the actual API response schemas and quotas. Offline archive audits now check the filename SHA256 prefix and report tampered files as invalid.

## Failure recovery and duplicate accounting

A checkpoint is read only if its archived snapshot still exists and matches the stored SHA256 digest. Archive writes precede checkpoint advancement; an archive write error leaves the prior checkpoint unchanged. The offline test suite simulates this failure and verifies that the same cursor is retried. This is **not** a process-kill or power-loss durability test, and concurrent runners still require an exclusive lock before production scheduling.

`ingestion.duplicates.duplicate_report(federated)` counts repeated provider identities `(connector, source_id, external_id)`, including repeats across archived snapshots. `ingestion.audit_archive.audit_directory` now includes these metrics under `duplicate_diagnostics`. No observation is deleted, merged or ranked, and shared canonical URL hints are **not** interpreted as corroboration from independent sources. The report is diagnostic only and is not an exactly-once delivery guarantee.

## Per-source concurrency lock

`ingestion.run_batch.run_pages` now holds a nonblocking advisory lock in the checkpoint directory for the entire read/fetch/archive/checkpoint transaction. A second worker for the same `(provider, source, scholarly date interval)` receives `SourceBusyError` **before making a request**; distinct source scopes can proceed concurrently. Locks use POSIX `fcntl.flock` and intentionally leave lock files in place. The OS releases the lock when the process exits.

**Deployment limits:** This protects only cooperating processes that share the same lock directory on a filesystem with reliable POSIX locking. It does not coordinate separate ephemeral runners, distributed workers, object storage, or Windows. It does not replace durable database transactions or exactly-once semantics. A production scheduler must provide shared durable storage and a distributed lease/lock or transactional claim mechanism. Do not delete lock files while workers may be active.

## Experimental transactional SQLite ledger (opt-in runner integration)

`ingestion/sqlite_ledger.py` introduces a **local prototype** for persistent, atomic acquisition state. It stores immutable JSON page payloads and provider observation identities in SQLite, with `BEGIN IMMEDIATE` transactions, WAL mode, an expiring owner lease, cursor updates committed together with each page, and idempotent replays of the same page payload. `metrics(db)` distinguishes stored observations from unique provider identities; it does not delete repeats.

The tests exercise lease contention, expiry, stale-owner rejection, duplicate page replay, failed validation, and reopening the database. This module is **opt-in through `run_pages(..., ledger=db)` or `--sqlite-ledger`**, does not write to Supabase, and does not authorize background ingestion. SQLite leases require careful TTL renewal during slow fetches; production multi-host operation needs a shared transactional database, fencing tokens and durable retention/deletion policy. Never treat this prototype as a production distributed lock.

## SQLite integration (manual opt-in, development only)

The bounded runner and heterogeneous experiment now accept an optional `ledger` connection. Without it they preserve the existing local append-only archive and POSIX lock behavior. With it, each page is committed atomically with the cursor in SQLite, under an expiring scope lease; the SQLite path does **not** write JSON archive files or local checkpoint files. Both paths retain provider metadata and do not perform editorial selection.

Dry runs make **no network calls** and do not open the database. Real API acquisition still requires `--live`:

```sh
python -m ingestion.run_batch crossref --source crossref-works --from-date 2026-10-09 --to-date 2026-10-10 --max-pages 2 --page-size 5 --sqlite-ledger data/discovery/ingestion.sqlite3
python -m ingestion.run_batch crossref --source crossref-works --from-date 2026-10-09 --to-date 2026-10-10 --max-pages 2 --page-size 5 --sqlite-ledger data/discovery/ingestion.sqlite3 --live
python -m ingestion.experiment config/ingestion-experiment.example.json --sqlite-ledger data/discovery/ingestion.sqlite3 --live
```

The SQLite experiment coverage report explicitly labels metrics as **cumulative ledger totals**; they are not the incremental output of just one experiment. `ingestion.audit_sqlite.audit_ledger(db)` verifies stored page hashes, normalized observation copies and checkpoint heads without contacting providers.

**Operational restrictions:** this is a local SQLite prototype, not Supabase or distributed cloud storage. The lease TTL is one hour in the runner and is not renewed during long operations. SQLite is unsuitable for independent ephemeral CI workers without shared durable storage. There is no scheduled job, cloud migration, reconciliation of deleted social posts, encrypted-at-rest deployment configuration, backup/restore exercise, or production authorization. Do not enable unattended production ingestion.

### Inspecting the local ledger safely

```sh
python -m ingestion.audit_sqlite_cli data/discovery/ingestion.sqlite3
```

The audit CLI opens an **existing** SQLite database in read-only mode; it will not create a new database or fetch from external services. It prints cumulative page and observation counts, repeat provider-identity counts, and any hash/content/checkpoint-head mismatches. Do not treat a passing audit as proof that all upstream source records were discovered or that a provider's records are accurate.

The integration suite also checks that two independent SQLite connections cannot acquire the same active source lease before making an API request. This does not replace multi-host PostgreSQL fencing or lease renewal.
