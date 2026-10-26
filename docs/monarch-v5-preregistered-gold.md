# Monarch S473/S474 — preregistered end-to-end v5 pilot

**Status:** gold expectations frozen before any v5 LLM calls. Do not send these labels to extraction or judge.

Input: original source records S473 and S474 from the frozen joint-results corpus. Verify original article text vs summaries before claiming full-text testing.

Expected per-source: independent study container event (even if no main news card), article date distinct from event date, three study details each `part_of` the study container, not `reacts_to`. Decline n4 is background/context, with no `part_of` to this study.

Expected cross-source judge: S473 study == S474 study; n0==n3, n1==n5, n2==n6. No equivalent event for n4; no unsupported detail conflicts.

Expected composer: exactly ONE matrix anchored to the merged study container, containing exactly three detail cards, each supported by S473 and S474; decline n4 outside as context/single-source item. A container may exist as an internal anchor without a separate displayed news card.

Validation: report per-source extracted event coverage, false/missing part_of, wrong reacts_to, context recall, 4 positive judge comparisons and negative n4 comparisons, final card/matrix counts, provenance fields, per-source and per-pair tokens and cost. A failed or incomplete API run must not be called a successful pilot.

No additional LLM calls for acquisition metadata or composition. Do not let gold influence extraction, judge or clustering.


## Amendment 2026-10-26 — independence and container identity
This amendment is recorded **after run 40414572740**, not retroactively before it. It is preregistered for the next run only.
- Container referent: the solar-powered Bluetooth monarch tracking **project**, with Florida/Caribbean and urban/industrial findings; no named authors, institution or journal established by the archived excerpts.
- S473/S474 have literal shared passages (n0/n3 and n1/n5). Mark **probable shared content origin**, even if publisher metadata is unknown. Do not assert a confirmed common agency or publisher.
- Expected data: one incident with three fact groups, two publication/source records per group; n4 outside as background.
- Expected feed: **single independent-origin presentation**, with "also republished by" / provenance warning, NOT a multi-independent-source matrix, unless subsequent evidence establishes independence.
- n2/n6: same core tracker-technology fact, with additional testing on insects and hummingbirds in n6. A judge split is not automatically wrong; evaluate core-overlap-plus-extra-detail and retain attribution.
- Independently of presentation, judge must identify the project container and link study details via part_of. No reaction link merely because technology enables tracking.
- Preserve previous run's results and usage as a diagnostic baseline; the revised outcome applies only to future runs.
