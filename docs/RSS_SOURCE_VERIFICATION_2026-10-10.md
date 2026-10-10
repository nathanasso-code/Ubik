# RSS source verification — actual GitHub Actions evidence, 2026-10-10

## Scope and reproducibility

Run: https://github.com/nathanasso-code/Ubik/actions/runs/38089426155
Branch: `develop/ubik-core`; workflow `ai-discovery-pilot.yml`; commit `9553859a`.
The workflow fetched the configured RSS/Atom feeds, ran offline normalization and source audit, and uploaded a 14-day `ai-models-discovery` artifact. This was **real network acquisition**, not a mock. No production database, main branch or scheduler was modified.

## Actual results

- Registry: **32 entries**; **24 enabled RSS feeds**, 8 disabled candidates.
- **19** feed requests succeeded; **5** failed.
- **2,638 normalized observations** from the successful feeds; this is a single run's accumulated result from an initially empty ephemeral workspace, **not** an estimate of new items per day.
- **17** successful feeds had at least one normalized observation; **2** successful requests produced zero.
- The workflow's inventory and unselected RSS federation/quality audit steps completed successfully.
- Raw upstream item counts were **not available in this first run**. A second live run with the new counter is documented below.

| Source ID | Result | Normalized observations |
| --- | --- | ---: |
| openai-news | success | 1287 |
| huggingface-blog | success | 876 |
| sebastian-raschka | success | 156 |
| google-deepmind | success | 100 |
| simon-willison | success | 30 |
| la-frontiere-economics-ai | success | 30 |
| arxiv-cs-ai | HTTP/feed succeeded; zero normalized | 0 |
| arxiv-cs-cl | HTTP/feed succeeded; zero normalized | 0 |
| the-batch | HTTP 403 | 0 |
| jack-clark | HTTP 403 | 0 |
| economics-of-ai | HTTP 403 | 0 |
| frankly-counterfactual | HTTP 403 | 0 |
| dan-luu | feed exceeds configured 3 MB bound | 0 |

Other successful feed observations contribute to the same 2,638 total; consult the run artifact for the full source-by-source table. Four failed HTTP 403 responses must **not** be treated as absence of publications or worked around through unauthorized access. The Dan Luu size error is a deliberate guardrail, not evidence the feed has no articles.

## Concentration and interpretation

OpenAI News and Hugging Face account for **2,163/2,638 ≈ 82.0%** of normalized observations in this run. This is source-volume concentration, **not** editorial importance or evidence of independent corroboration. Many older entries may be included: no 24-hour publication window was imposed on the RSS fetch. Do not interpret this as a daily throughput figure.

Two arXiv RSS feeds returned zero normalized records. The follow-up live run below confirms that both returned **zero raw entries**, so the normalizer did not discard their records in that run. The cause of the empty upstream feeds remains unverified.

## What the experiment does and does not prove

It proves that the configured pilot can make live RSS requests, normalize thousands of observations, preserve per-source statuses, federate without editorial selection and produce audit artifacts. It does **not** establish complete publisher coverage, independence of news lines, freshness distribution, availability of all 32 registry entries, or successful acquisition of all sources contemplated for Ubik. It does not yet verify live Hacker News, GDELT, Reddit, YouTube or a broad social firehose in the same run.

## Immediate engineering follow-up

1. Compare `raw_entries` and `seen` in the next run to diagnose arXiv and other losses.
2. Investigate feed-specific 403 conditions and documented public alternatives only when authorized; preserve original failure codes.
3. Investigate Dan Luu size limits with a safe bounded streaming/parser design rather than unbounded downloads.
4. Report source concentration, publication-age buckets, missing attribution, explicit language unknowns, duplicates and independent source lineage separately.
5. Expand the source registry into a cross-topic catalog **before** claiming that the full previously discussed source set is covered.
6. Defer source/card/nucleus selection until the acquisition evidence is evaluated.

## Follow-up live verification: raw versus normalized RSS entries

Second successful run: https://github.com/nathanasso-code/Ubik/actions/runs/38089481756 (commit `3002fc46`). The workflow again tested all 24 enabled RSS feeds.

- **19 successes**, **5 failures** with the same source IDs and error categories as above.
- **2,638 raw RSS/Atom entries** across successful feeds; **2,638 normalized observations**. Thus **zero records were dropped by normalization** in this run, for feeds that returned data successfully.
- Both `arxiv-cs-ai` and `arxiv-cs-cl` returned **0 raw entries and 0 normalized entries**; this is not a parser rejection. Feed configuration, upstream publication cadence and endpoint behavior still need investigation.
- The successful source distribution remained the same; these runs are near-contemporaneous independent invocations, **not** 5,276 distinct records or two days of output.
- Failed feeds were not included in the raw-entry denominator; 403 and size-cap errors remain unresolved.

## Freshness timestamp parsing correction

The source quality audit now recognizes both ISO-8601 dates (common in Atom/API metadata) and RFC 2822 dates (common in RSS `pubDate`). Before this change, many valid RSS publication timestamps would have been classified as unknown. A deterministic regression test checks `Thu, 08 Oct 2026 10:00:00 GMT`. Existing historical audit reports must be regenerated to obtain corrected freshness distributions.

## Attribution completeness in the same live RSS run

The 2,638 normalized observations included **163 entries with an author named in feed metadata** and **2,475 without a named author** (about **93.8%** missing). All 2,638 had a nonempty publication-date field and an original link according to the feed report, but these fields are **not yet independently verified**. A nonempty date string is not necessarily parseable or correct. Named feed authors are not proof of verified authorship. This is a metadata-quality diagnostic, not a reason to exclude a source from acquisition.
