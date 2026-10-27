Ukraine v5 non-regression preregistration

Run after reviewing frozen monarch rejudge 40421847220. Preserve v4 corpus and original gold unchanged. Re-extract each Ukraine source independently using v5, then E5-small top-5 candidate retrieval, four-way judge (equivalent, distinct, uncertain, part_of with direction), and conservative composition. No gold in prompts.

Hard checks: executive order one identity group with four source records; zero diesel-agreement/executive-order merges; no deterioration relative to v4 identity decisions; separate truce acts and reactions. Reader-facing matrix requires at least two independent origins, not merely two publications.

Additional checks: senator and Zelenskyy criticism positions, Dmitriev support position only when supported by original evidence; diesel referenced-event identity evaluated without forced agreement; single-source fragments retained without matrix status; no context-only incident merge. Report missing evidence as unknown.

Measure candidate recall before judgment, including role-disagreement misses; preserve one event per source per identity group and permanent distinct veto. Report all calls, tokens, costs, pair judgments, conflicts and provenance. Do not tune rules on Ukraine gold; correct only documented implementation bugs.

## Addendum before Ukraine v5
- Freeze expected presentation per incident: visible matrix (2+ independent origins), candidate incident (coherent but not eligible for visible matrix), single source (one origin even if republished). Report missing gold labels, never infer them from v5 output.
- Reuse existing Sonnet v4 outputs, do not rerun v4. Use the same exact model and configuration for v5 extraction and v5 judge; record any remaining v4/v5 model confound.
- No reaction position metric: v5 has no such field. Evaluate only recorded reaction target and mention/reaction distinctions.
- Test whether one cross-source part_of bridge connects diesel agreement and US executive order; distinguish distinct-card incident merger (weight 1 if adjacent) from card identity merger (weight 3), and unrelated incident bridge (weight 3).
- Measure complete per-source v5 cost (extraction plus attributed judging) against comparable v4 per-source cost; missing baseline means 2x gate unproven.
- Display each part_of edge once, retaining all origins; remove transitive child-to-ancestor edges only in presentation, never from evidence graph. Republished sources count as one independent origin.
- Without summaries, score the strict error-weight column; mark contradiction/position sentence coverage as not evaluated.
