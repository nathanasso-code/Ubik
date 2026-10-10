# First bounded live ingestion verification — 2026-10-10

## Scope

Two **one-time**, branch-only GitHub Actions workflows were executed on `develop/ubik-core` and removed immediately afterward. No production database, scheduler or main branch was modified. Both used the public metadata adapters, a single page per provider, at most five records per page, ephemeral local archives and offline federation audits.

## Evidence

| Provider | Scope | Result | Observations | Archive / federation errors |
| --- | --- | --- | ---: | --- |
| Crossref | Works, publication dates 2026-10-09 through 2026-10-10 | Successful HTTP/API acquisition | 4 | 0 / 0 |
| OpenAlex | Works, publication dates 2026-10-09 through 2026-10-10 | Successful HTTP/API acquisition | 5 | 0 / 0 |
| Bluesky | Public author feed for `bsky.app` | Successful HTTP/API acquisition | 3 | 0 / 0 |
| Mastodon | `mastodon.social` public local timeline | **Failed: HTTP 422** | 0 | Not archived |

Scholarly verification: https://github.com/nathanasso-code/Ubik/actions/runs/38087169646

Social verification: https://github.com/nathanasso-code/Ubik/actions/runs/38087200025

**Total successfully acquired observations: 12.** This is a smoke test, not a representative sample. Scientific date filtering and Bluesky author-feed scope are fundamentally different acquisition universes; counts must not be compared as coverage rankings. Zero federation errors refer only to successful archived pages.

## Findings and follow-up

1. Crossref, OpenAlex and Bluesky successfully completed live network acquisition, archive creation and federation/audit under small limits.
2. Mastodon returned HTTP 422 on the selected instance. The response body was intentionally not retained in logs; the cause is **unknown**. Investigate the API request contract, instance policy and authentication before any production use. Do not silently treat this as zero available posts.
3. The temporary workflows were deleted to prevent repeated automatic network calls on subsequent pushes. The separate manual-only smoke workflow remains on the development branch and is not yet dispatchable from the default branch.
4. The live experiments did **not** validate multi-page pagination, long-term checkpoints, deleted-content reconciliation, representativeness, source independence, licensing compliance, or unattended scheduling.
5. Social content previews are currently stored in ephemeral archive files during execution. Production retention policy, opt-outs and deletion reconciliation remain open requirements.

## Mastodon API contract review

The official Mastodon timeline documentation confirms that `GET /api/v1/timelines/public` supports `limit`, `local`, and `max_id` (https://docs.joinmastodon.org/methods/timelines/). Thus the observed HTTP 422 is **not yet evidence of an invalid query parameter**. Public preview can be disabled by an instance and some instances require authentication. The earlier experiment logged only the HTTP status, not the response body or a trace ID, so its exact cause remains unknown. Do not bypass an instance's access controls or automatically switch to authenticated scraping.

The next controlled diagnostic should compare a single request on the same instance with and without `local=true`, inspect sanitized server error codes (never tokens or post bodies), and test another explicitly approved public instance only if permitted. Keep results at one page and a small request budget.

## Pagination correction

A connector may discard returned records (for example, boosts, missing fields or non-public statuses) yet still receive a valid provider cursor. A zero-length **normalized** observation list therefore does not prove that the provider has reached the end. The bounded batch runner now follows a new cursor even on an empty normalized page, subject to its request budget, and stops if the cursor repeats. This avoids silently truncating discovery because of normalization filters.
