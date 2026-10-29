# Ubik v5.1 — Ukraine diagnostic: results (2026-10-29)

Protocol: `protocols/ubik-v5.1-ukraine-protocol.md` (commit a254300, before any call). All inputs and
outputs are in this folder with SHA-256 in `SHA256SUMS`. Ukraine is diagnostic; promotion is decided on
the AI corpus with the common criterion of 2026-10-28 08:20.

## Runs

| Stage | Run | Result | Cost (USD) |
| --- | --- | --- | --- |
| Extraction (Sonnet 5.5) | 40787687376 | 9/9 sources, 36 events, 0 errors, 0 post-hoc flags | 0.1038 |
| Blind mapping | — | 36 rows; independent reviewer agreed 34/36; S408:e6 scored in two readings | 0 |
| Candidate pairs | ukraine-v51-pairs | 126 pairs (E5-small, v5 parameters) | 0 |
| Judge Sonnet 5.5 | 40788784732 | 126/126, 2 invalid after retry | 0.5146 |
| Judge DeepSeek V4.1 Flash | 40788784732 | 126/126, 0 invalid, 0 reasoning tokens | 0.0248 |
| Cascade (simulated from the two runs) | — | 30 pairs to Sonnet | 0.1416 + 0.0248 |

## Weighted error vs reference (same formula for v5 and v5.1)

Formula (declared in `ingestion/ubik_ukraine_v51_evaluate.py`): 2 x split vicende (once each) +
3 x false card merges + 1 x extra cards per identity class. v5 events were mapped from the v5 extraction
only, after the fact, for comparison.

| Arm | v5 | v5.1 reading 1 (e6 = A) | v5.1 reading 2 (e6 excluded) | Weight-3 errors | Pipeline cost | x v4 |
| --- | --- | --- | --- | --- | --- | --- |
| Sonnet 5.5 | 14 | 10 | 9 | 0 | 0.618 | 1.84 |
| DeepSeek V4.1 Flash | 14 | 11 | 10 | 1 (S188:e3 + S433:e3) | 0.129 | 0.38 |
| Cascade DeepSeek -> Sonnet | — | 10 | 9 | 0 | 0.270 | 0.80 |

- Sonnet v5.1: the diesel-deal card now holds five of the six events (v5: two); A splits in 3 containers
  (v5: 4). C and D remain split.
- DeepSeek v5.1: C and D unified, A in 2 containers, but it merges the joint criticism by Zelenskyy and
  European leaders (A6) with Zelenskyy's criticism of the diesel deal (A2): a weight-3 false merge, the
  same family as the V3.2 failure. As a standalone judge it does not pass to the AI corpus.
- Cascade: every pair DeepSeek did not call distinct goes to Sonnet; the false merge is caught. In 6
  pairs DeepSeek says distinct where Sonnet says uncertain (lost candidate links); none where Sonnet says
  equivalent.

## Predictions (registered 2026-10-28 09:45)

| N. | Outcome |
| --- | --- |
| 1 No A/B merge | Confirmed for both judges |
| 2 More uncertain A/B pairs | Confirmed in reading 1 (Sonnet 4 vs 3, DeepSeek 3 + 1 equivalent vs 1); not in reading 2 |
| 3 Diesel vicenda less fragmented | Confirmed (Sonnet 3 or 2 containers vs 4) |
| 4 n14 and n27 recovered as reactions | Half: n14 yes, n27 still a mention |
| 5 No EU diesel agreement | Confirmed (EU mentions only in von der Leyen pairs) |
| 6 DeepSeek loses more on A/B | Confirmed weakly: one A/B equivalent verdict (S383:e1-S408:e6, reading 1), not merged |
| 7 Cost within +-20% | Partly falsified: extraction -31%; judges -13% (Sonnet) and -9% (DeepSeek) |

## Reading

Removing the sample hints did not produce A/B confusion and reduced fragmentation: the hints were
hurting more than helping. With clean prompts the Sonnet procedure is within the 2x cost ceiling, and
the cascade matches Sonnet's quality at 0.80 x v4. These are diagnostic results on 24 news items built
from LLM summaries; the decision is taken on the AI corpus.
