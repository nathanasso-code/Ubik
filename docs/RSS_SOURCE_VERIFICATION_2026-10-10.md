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
- Raw upstream item counts were **not available in this run**; a later code change adds them to per-feed reports.

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

Two arXiv RSS feeds returned zero normalized records. Without upstream raw-entry counts, one cannot yet tell whether the feed was empty or records were dropped by normalization. The follow-up implementation records both `raw_entries` and `seen`.

## What the experiment does and does not prove

It proves that the configured pilot can make live RSS requests, normalize thousands of observations, preserve per-source statuses, federate without editorial selection and produce audit artifacts. It does **not** establish complete publisher coverage, independence of news lines, freshness distribution, availability of all 32 registry entries, or successful acquisition of all sources contemplated for Ubik. It does not yet verify live Hacker News, GDELT, Reddit, YouTube or a broad social firehose in the same run.

## Immediate engineering follow-up

1. Compare `raw_entries` and `seen` in the next run to diagnose arXiv and other losses.
2. Investigate feed-specific 403 conditions and documented public alternatives only when authorized; preserve original failure codes.
3. Investigate Dan Luu size limits with a safe bounded streaming/parser design rather than unbounded downloads.
4. Report source concentration, publication-age buckets, missing attribution, explicit language unknowns, duplicates and independent source lineage separately.
5. Expand the source registry into a cross-topic catalog **before** claiming that the full previously discussed source set is covered.
6. Defer source/card/nucleus selection until the acquisition evidence is evaluated.
