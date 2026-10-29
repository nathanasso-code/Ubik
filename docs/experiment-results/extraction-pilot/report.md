# Extraction cost pilot — results (2026-10-29)

Protocol: `protocols/ubik-extraction-cost-pilot.md`. Inputs, outputs, the blind reference and the blind
evaluation stay in the private corpus repository (`reports/extraction-pilot/`), because they derive from
full article texts. Only figures are reported here.

## Run

- Stopped at the cost ceiling after 12 of 14 articles. Total 0.465 USD; the ceiling was 0.45 and the check runs
  after each call.
- The preflight estimate (0.40 USD) was wrong. Sonnet extraction of full texts costs 0.030 USD per article, about
  twice the unit cost derived from the earlier probe, because output tokens dominate (about 2300 per article).
  The unit costs are corrected in `ingestion/ubik_cost_guard.py`.
- Sonnet returned malformed JSON twice on one article (X03), so it has 11 valid articles. DeepSeek returned
  no invalid answers.

| Arm | Cost per article | vs S-full | Valid | Events (median / total) | Primary correct (yes / partial / no) | Reference context events recalled |
|---|---|---|---|---|---|---|
| S-full (Sonnet, 6000 chars) | 0.0299 USD | 1 | 11/12 | 9 / 105 | 9 / 2 / 0 | 18/18 |
| D-full (DeepSeek, 6000 chars) | 0.0026 USD | 1/11.6 | 12/12 | 11 / 141 | 9 / 1 / 2 | 20/20 |
| D-lede (DeepSeek, ~1500 chars) | 0.0013 USD | 1/23 | 12/12 | 6.5 / 73 | 8 / 2 / 2 | 7/20 |

On the 11 articles common to all arms:

| Arm | Primary correct (yes / partial / no) | Context events recalled |
|---|---|---|
| S-full | 9 / 2 / 0 | 18/18 |
| D-full | 8 / 1 / 2 | 18/18 |
| D-lede | 7 / 2 / 2 | 6/18 |

The evaluator found no hallucinated events in any arm.

## Errors

- **D-full.** Both "no" cases are a null primary on an opinion or analysis piece where the reference names a
  main fact. One of the two articles is off-perimeter.
- **S-full.** The "partial" cases took a consequence, or a ruling the article argues about, as primary instead
  of the article's own act.
- **D-lede.** It loses most context events, which sit beyond the first ~1500 characters.

## Predictions

1. D-lede ≤ 1/10 of S-full cost — **confirmed** (1/23).
2. D-full ≤ 1/8 — **confirmed** (1/11.6).
3. D-lede ≤ 60% of S-full events — **falsified** (72%).
4. Primary correct ≥ 12/14 (S-full) and ≥ 11/14 (DeepSeek arms) — **not met by any arm** on strict "yes".
   - Rates: 82% S-full, 75% D-full, 67% D-lede, against thresholds of 86% and 79%.
   - The sample is incomplete (11–12 articles).
   - Counting "partial" as correct, S-full and D-full would pass.
5. Context recall: S-full ≥ 70%, D-full within 15 points, D-lede ≥ 20 points below — **confirmed** (100%,
   100%, 35%).
6. DeepSeek ≤ 2 invalid answers per arm — **confirmed** (0).

## Decision (per the preregistered rule)

- **D-full** matches Sonnet on context events and validity at 1/11.6 of the cost. It falls slightly short on
  primary events (two null primaries). It becomes the candidate extractor, to be confirmed on a larger sample
  with judges and composition before adoption.
- **D-lede alone** is not enough: it keeps most primary events but loses two thirds of the context events.
- **Judging is now the dominant cost.** D-full also produces about 34% more events than Sonnet, so more pairs.
