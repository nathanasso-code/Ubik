Ukraine v5 non-regression preregistration

Run after reviewing frozen monarch rejudge 40421847220. Preserve v4 corpus and original gold unchanged. Re-extract each Ukraine source independently using v5, then E5-small top-5 candidate retrieval, four-way judge (equivalent, distinct, uncertain, part_of with direction), and conservative composition. No gold in prompts.

Hard checks: executive order one identity group with four source records; zero diesel-agreement/executive-order merges; no deterioration relative to v4 identity decisions; separate truce acts and reactions. Reader-facing matrix requires at least two independent origins, not merely two publications.

Additional checks: senator and Zelenskyy criticism positions, Dmitriev support position only when supported by original evidence; diesel referenced-event identity evaluated without forced agreement; single-source fragments retained without matrix status; no context-only incident merge. Report missing evidence as unknown.

Measure candidate recall before judgment, including role-disagreement misses; preserve one event per source per identity group and permanent distinct veto. Report all calls, tokens, costs, pair judgments, conflicts and provenance. Do not tune rules on Ukraine gold; correct only documented implementation bugs.
