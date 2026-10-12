# Mastodon discovery pilot (2026-10-12)

## Scope and status
New opt-in discovery module: `ingestion/mastodon_discovery.py`.
This extends the existing metadata-only acquisition boundary without changing UI, topic selection, publication or production deployment.

Four source scopes: local public timeline, remote/federated timeline, hashtag timeline, and known instance-local account ID.
Each call retrieves at most 40 statuses; only explicitly public non-boost statuses become observations. Preserve original ActivityPub URI as external identity when supplied, along with source URL and discovery endpoint. Status HTML is **not** archived. No automated account or instance crawling.

## Execution
Dry-run (no network):
```sh
python -m ingestion.mastodon_discovery --instance mastodon.social --approved-instances config/mastodon-instances.pilot.json --mode tag --tag science
```
Single live page, **only after reviewing the instance rules and network egress controls**:
```sh
python -m ingestion.mastodon_discovery --instance mastodon.social --approved-instances config/mastodon-instances.pilot.json --mode tag --tag science --limit 10 --live
```
Other modes: `--mode local`, `--mode federated`, `--mode account --account-id 123` (ID must be discovered legitimately on that instance). This is not an authenticated full-text search API.

## Validation and constraints
Run `python -m unittest tests.test_mastodon_discovery` and then the complete suite.
The originating execution environment cannot resolve mastodon.social (DNS error); **no successful live acquisition has been verified**. The five instance hostnames are candidates, **not confirmed accessible or approved by their administrators**. Review instance terms and operator permissions before enabling each.

Per-run collection remains one bounded request; no 24-hour monitoring, rate-limit header integration, automatic discovery, deletion reconciliation, or production scheduler is claimed. The existing transport handles 429/5xx retries with bounded backoff; per-instance budgets, shared cloud persistence, safe DNS/redirect egress, and status deletion/recheck are required before scaling.

Avoid treating a federated server's timeline as a census. Cross-instance appearances of one ActivityPub URI are not independent evidence. Do not retain private/direct/followers-only or unlisted content, and do not republish author text without appropriate rights review. Source visibility and deletion can change after collection; public-only filtering does not itself solve data-protection obligations.

## Next verification
1. Execute offline tests in CI.
2. Validate 5 instances × 3 modes (local, federated, hashtag) over a limited, consent/terms-reviewed window; record HTTP outcomes, API quotas, pagination, error and duplicate rates.
3. Add stable cursor polling, deletion handling, operator-controlled account scopes, and compliance checks before any recurring job.
4. Keep acquisition separate from editorial selection and topic clustering.
