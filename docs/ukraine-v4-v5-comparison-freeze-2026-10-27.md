# Ukraine v4/v5 comparison freeze — 2026-10-27
Committed before inspecting any v4 level-2 results or calculating v4 scores.

## Rules
- v5 frozen: 8 incidents, 3 matrices, 12 Topic cards, 0 bridge edges, no LLM calls; S188:e3 belongs to both target incidents without merging them. Do not change v5 until comparison.
- Split incident error: weight 2 **once per split reference incident**, irrespective of extra fragments, applied identically to v4 and v5. Clarification is post-v5 observation, not original preregistration.
- Primary: actual complete historical v4 procedure versus frozen complete v5 procedure, representing rollback decision.
- Secondary: each frozen extraction and judge output through the **same current composer**, including multi-target reactions.
- Apply original frozen decision rule, weight-3 nonincrease guardrail, and v4 wins ties.
- Report coverage, relation correctness, card identity; for each report recovered errors, missed errors and controls. Distinguish candidate recall from judged equivalence.

## v5 observations, do not correct
- Diesel agreement A appears as two matrices: S382/S387/S433 and S188/S383; score one split A, and record presentation defect. S188:e2 never compared to primary A events: retrieval failure.
- Independence of S188 and S383 remains provisional, must verify before public presentation (two of three matrices rely on these sources).

## Original v4 judgments first
Search existing GitHub Actions artifacts for v4 level-2 judgments (historically about USD 0.002/pair). Frozen v4 extraction artifact 12591716174 is NOT itself judge output. If unavailable, rerun **unchanged** historical v4 judge prompt, model, and retrieval on frozen extraction, label rerun rather than original, and commit an explicit dollar cap before execution. Rerun variability matters for small differences.

## Secondary adapter mapping (frozen before v4 inspection)
- card.id: deterministic prefix card: plus first event ID from the existing v4 judge equivalence group.
- card.events: original event IDs in the group, no synthetic IDs.
- card.source_ids: explicitly represented source IDs in those event IDs; do not infer independence.
- card.independent_origin_ids: only if explicitly present; otherwise omit and mark provenance provisional.
- reacts_to relations: only explicit v4 assignment reaction links, mapped via event-to-card lookup.
- part_of relations: only explicit v4 part_of links if any; otherwise empty, no inference.
- event nature and other missing fields: omitted or empty, never invented.
- No rejudging, re-retrieval, or model calls during adaptation.

## Order
1. This standalone rules commit.
2. Search original v4 judgments.
3. If needed, separate preregistered spend cap and exact v4 judge rerun.
4. Primary weighted score and weight-3 guardrail.
5. Secondary same-composer comparison.
6. Three-dimension auditable report; tie retains v4.
