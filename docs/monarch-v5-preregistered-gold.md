# Monarch S473/S474 — preregistered end-to-end v5 pilot

**Status:** gold expectations frozen before any v5 LLM calls. Do not send these labels to extraction or judge.

Input: original source records S473 and S474 from the frozen joint-results corpus. Verify original article text vs summaries before claiming full-text testing.

Expected per-source: independent study container event (even if no main news card), article date distinct from event date, three study details each `part_of` the study container, not `reacts_to`. Decline n4 is background/context, with no `part_of` to this study.

Expected cross-source judge: S473 study == S474 study; n0==n3, n1==n5, n2==n6. No equivalent event for n4; no unsupported detail conflicts.

Expected composer: exactly ONE matrix anchored to the merged study container, containing exactly three detail cards, each supported by S473 and S474; decline n4 outside as context/single-source item. A container may exist as an internal anchor without a separate displayed news card.

Validation: report per-source extracted event coverage, false/missing part_of, wrong reacts_to, context recall, 4 positive judge comparisons and negative n4 comparisons, final card/matrix counts, provenance fields, per-source and per-pair tokens and cost. A failed or incomplete API run must not be called a successful pilot.

No additional LLM calls for acquisition metadata or composition. Do not let gold influence extraction, judge or clustering.
