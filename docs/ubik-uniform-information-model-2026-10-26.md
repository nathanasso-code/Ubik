# Ubik uniform information model — implementation decision 2026-10-26

Authoritative product reference: user-provided “Ubik — Modello informativo” (six-page PDF, 2026-10-26). This note supersedes conflicting portions of earlier v5 contracts; do not modify main.

## Corrected semantics
- An **incident/vicenda** is an always-existing referent-centered data entity, even with one source. The two-independent-source threshold is **presentation only**, not existence or retention.
- **Cards** hold same-fact corroboration and distinct details; source identities remain visible. A card is not a substitute for a source.
- `part_of` and `reacts_to` attach facts to incident referents; `mentions` and background context do not attach.
- A source can belong to multiple incidents. No age cutoff: all incidents stay searchable. Merges are symmetric and preserve aliases/redirects; uncertainty remains candidate relation, not merge.
- The feed shows a matrix for multi-independent-source incidents, corroborated fact cards with sources, and single-source items with visibly distinct points.
- **Live/static** is computed from new independent sources, positions, open conflicts and editorial override, with bidirectional transitions; use explicit recency policy and avoid automatically labeling a one-source incident live.
- Incident summaries are attributed fact/position/conflict projections with fact/source references per sentence, regenerated only on significant structural change, retaining versions. Topic summaries aggregate incidents.
- Topic scope editorial; decide AI corpus Topic(s) before gold; final pilot deliverable is reader-facing Topic page.
- Acquisition carries source_type, provenance, editorial_group_id, content_origin, explicit unrated default; do not conflate number of publishers with independent confirmations.
- Self-declaration inference is deferred.
- Community, tags and social ingestion deferred.

## Monarch gold (unchanged)
S473 and S474: study container event equivalent across sources; n0=n3, n1=n5, n2=n6, each detail part_of study; n4 context outside study. **One displayed matrix** for the study, **one retained background/single-source incident or context record** for decline; never erase the latter from the data model.

## Ukraine review correction
The six diesel comparisons are among the *referenced agreement events* from S188, S382, S383, S387, S389, S433, not reaction cards. Truce pair concerns referenced events S382/S387; n11, n12, n20 are distinct facts with reacts_to. Refinery case n27 was unidentifiable, not an incorrectly merged event. Do not claim otherwise.

## Execution gates
1. Update composer/tests and acquisition provenance.
2. Freeze v5 extraction and conflict-aware pair judge prompts and data contracts.
3. Run monarch S473/S474 end-to-end from independent original input; report API calls and tokens, not merely structural fixture.
4. Decide AI topic boundaries, create human gold, run AI corpus, render reader-facing Topic page.
