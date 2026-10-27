# Ubik v5 schema freeze and preregistered comparison
Status: preregistered before Ukraine v5 and AI corpus tests. Experimental branch only; main unchanged.

## Schema freeze
- Events have separate event_nature (container|fact) and text_role (narrated|referenced). Validate closed vocabularies.
- Directed event_part_of lives ONLY in event registry, child -> parent, with source evidence. Do not infer from mentions.
- News assignments retain news_key, primary_event_id, reacts_to with position, mentions, context_only. Remove part_of from assignments. Main event must be the most specific event narrated; duplicate primary_event_id within a source is a warning requiring review, not automatic merger.
- Local model IDs are provisional; deterministic source-scoped canonical IDs and remapping of every relation are done by code.
- Cross-source candidate retrieval uses E5-small top 5 with soft nature penalty, never a categorical nature veto. High-similarity cross-nature pairs remain eligible. Fix a single ranking rule before evaluating Ukraine; do not tune against gold.
- Judge returns equivalent, distinct, uncertain, part_of with direction; source evidence preserved; no hierarchy inference from mentions.
- The above fields and categories are frozen until after both Ukraine and AI corpus evaluation; only documented implementation bug fixes allowed.

## Sequential gates
1. Rejudge latest monarch extraction with soft filter and new event-level relations, report candidate coverage and whether technology S474 links to project through S473. Do not merge unrelated roots within a source.
2. Ukraine v5 complete extraction, judge and composition; non-regression against frozen v4 gold. Executive order four source records, zero diesel/order merges, referents not worse than v4; reactions and independent-origin matrices assessed.
3. AI corpus: evaluate v4 and v5 on identical material with frozen criteria, costs, retrieval recall, identity errors, false merges and reader presentation.

## Decision rule
v4 is rollback baseline. If v5 worsens referent recall or precision on Ukraine, retain v4 as primary and cherry-pick only independently demonstrated v5 benefits (container, context, shared-origin detection). On AI corpus prefer v4 unless v5 is clearly better on the preregistered metrics; avoid post-hoc optimization.

## Additional ex-ante monarch expectations
- S473:e0 and S474:e1 project containers should be equivalent.
- S473:e5 and S474:e5 solar technology must be retrieved as a candidate despite divergent nature classifications; acceptable verdict equivalent or directional part_of, subject to evidence.
- The second S474 root should connect to the project through cross-source links, without forced within-source fusion; if disconnected, record a documented limitation, not an automatic failure.
- Retrieve the three factual pairs: transmitters, migration routes, Bluetooth. Preserve the population decline outside the project incident.
- Score duplicate primary events for distinct news within the same source as **level-1 extraction errors**, not merely warnings; inspect S473 n1 explicitly.

## Quantitative AI corpus gate
On the SAME frozen AI corpus, v5 replaces v4 **only if all three conditions hold**:
1. v5 strictly improves at least one primary measure: referent correctness, primary-fact correctness, or correct identity pairs within groups.
2. v5 does not reduce merge precision (no increase in incorrect mergers, measured on the same adjudicated pairs).
3. v5 per-source total pipeline cost is <= 2.0 times v4 per-source cost, including extraction and attributed candidate-judgment costs.
Report numerators, denominators, abstentions, costs, and the actual comparisons. If any condition fails or is not measurable, retain v4. This gate does not override the earlier Ukraine non-regression requirement.
