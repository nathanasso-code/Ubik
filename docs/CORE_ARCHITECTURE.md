# Ubik Core Architecture — first extraction

Development branch: `develop/ubik-core`. This is intentionally **not** a production release.

## Separation rules
1. Data records (`topic`, `claim`, `event`, `source`, `evidence`, `relation`, `revision`, `contribution`) are independent of pages and views.
2. Views (`map`, `timeline`, `chart`, `comparison`, `archive`, `sources`, `evidence`, `discussion`) are optional. No view owns canonical evidence.
3. Topics declare capabilities and datasets; they are not hardcoded navigation tabs or parents of other topics.
4. The existing attack corpus is not migrated or overwritten. `projectEvent` creates a non-destructive view of legacy records.
5. A schema change requires a version and a migration plan. Keep raw source records and revision history.
6. Do not generalize a one-off UI before a second use case demonstrates shared structure.
7. A source publisher count is not an independence count; source genealogy is a separate evidence relation.

## Current status
`assets/ubik-core.js` implements pure dependency-free contracts and a validated topic registry. `assets/topic-registry.js` consumes it. The existing app still renders with its old specialized functions: extraction is incremental and **not complete**.

## Release discipline
Work on this branch; run `node tests/ubik-core.test.cjs`, syntax-check all JS, then manually inspect topic navigation, map, timeline, search and provenance. Merge only after regression checks. One production deployment per coherent release, not per commit.

## Temporal extraction
`assets/temporal.js` provides date validation, month boundaries, monthly counts and independent filter state. The attack topic now consumes it through `attackTime`; map, campaign and archive continue to share the same selected range. Run `node tests/temporal.test.cjs` before release. The live feed is deliberately outside the historical date filter.

## Next extraction
- shared SourceCard, ClaimCard, RevisionList, ProvenanceView;
- topic-specific adapters for temporal datasets beyond attacks;
- reusable MapView receiving records and configuration, not reading global `attacks`;
- topic discovery through search and semantic links; no fixed topic header.
