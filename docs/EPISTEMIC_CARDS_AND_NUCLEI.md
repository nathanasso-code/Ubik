# Epistemic cards and persistent nuclei — product decision record

Status: **reconstruction of the October 8, 2026 product discussion**, not a production specification or implemented feature. Primary historical source: `ChatGPT-Ubik Product Audit-20261010-2103.pdf`, approximately pages 358–371. Recheck the original discussion before treating later details as final decisions.

## Current direction, replacing older navigation assumptions

Pulse, Press and Insights were early section concepts and are **not the current required information architecture**. Do not reintroduce them as mandatory tabs, data types or delivery milestones. The product's underlying objects and their relations take precedence over navigation. The separate Radar / Verification / Scrigno exploration likewise must not be mistaken for immutable navigation.

## Distinct objects

1. **Source/document** — original article, paper, announcement, post or native contribution, with preserved author/publisher, original URL and provenance. Multiple observations of one URL are not independent evidence.
2. **Informational cluster** — recomputable grouping of publications about substantially the *same occurrence*, not merely the same topic. Keep source membership and eventual merge/split lineage.
3. **Epistemic card** — economical, usually automatic presentation of a cluster or standalone primary source. Reduces feed redundancy; it need not become a debate or undergo validation. Most cards may have a short period of prominence while remaining retrievable.
4. **Persistent nucleus** — stable identity and scoped question/issue that can connect multiple cards, original sources, arguments and revisions over time. A nucleus may appear in multiple topics without duplicating its identity or discussion.
5. **Debate** — selectively activated capability attached to an eligible published nucleus; not an automatic property of a card or cluster.
6. **Validation** — distinct, evidence-grounded and comparatively rare process; publication, debate activation and validation are **not synonyms**.

## Provisional lifecycle

The discussion proposed candidate → checked/reviewed → published nucleus → debate enabled as distinct steps, with selective debate activation. The current `assets/knowledge-pipeline.js` implements `candidate → reviewed → published → archived` plus separate `enableDebate` guard. These are deterministic contract checks, **not** editorial authorization, moderation, verification, persistence or UI.

Promotion signals under consideration: distinct information origins, persistence over time, divergence of evidence, topical relevance and meaningful community interest. Raw source volume and popularity alone are insufficient. A user may also propose a nucleus directly, subject to duplicate/scope checks.

## Invariants for the pilot

- Never equate a card, a cluster and a nucleus.
- Do not merge distinct events simply because they share keywords or a subject.
- Do not count syndication as independent corroboration.
- Re-clustering must not change a nucleus ID or strand human contributions.
- A published nucleus need not have an active debate or a validation badge.
- A card can be useful without being promoted to a nucleus.
- Preserve original authorship and source provenance.
- Treat topic memberships as associations, not duplicated objects.

## Verified repository state (October 10, 2026)

- `assets/knowledge-pipeline.js`: source normalization, provisional clusters, nucleus proposal/state transitions, topic guard and debate enablement.
- `tests/knowledge-pipeline.test.cjs`: basic contract checks, not integration coverage.
- `docs/KNOWLEDGE_PIPELINE.md`: explicit experimental scope.
- `docs/CORE_ARCHITECTURE.md`: topic/claim/event/source/evidence/relation/revision/contribution data model, views independent of canonical records.
- RSS/Atom pilot discovers source observations, **not** operational clustering, epistemic card publication, nucleus persistence, debate moderation or validated knowledge.

## Next verifiable experiment

Build an **offline, reversible fixture-driven evaluation** before wiring public UI: (a) same story from multiple feeds → one provisional cluster/card, (b) similar topic but distinct event → separate cards, (c) several related cards → candidate nucleus with explicit reason, (d) updated cluster membership → unchanged nucleus identity, (e) no automatic debate or validation. Record false merges, missed merges, redundant nucleus proposals and provenance loss. Any automatic proposal mechanism remains a hypothesis until evaluated.

## Open product decisions

- Precise identity/scope rules and merging or splitting of persistent nuclei.
- Which evidence and safeguards justify automatic publication versus editorial review.
- Who can activate debates, how moderation works and when validation can be granted.
- Whether the term “epistemic card” remains the final user-facing label.
- How to represent the relationship between a card, a nucleus and a primary document in the interface.

This record corrects stale references to Pulse/Press/Insights as mandatory sections. It does not claim those historical concepts are permanently abandoned.
