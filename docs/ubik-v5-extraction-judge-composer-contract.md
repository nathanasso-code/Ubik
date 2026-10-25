# Ubik — Extraction v5, pair judge v5, matrix composer v5 (draft contract)

Status: experimental specification; **not** a completed LLM pilot. Preserve frozen v4 and existing gold untouched.

## 1. Extraction v5 — one request per source
Return `source_id`, `article_published_at`, `events[]`, `news[]`, `assignments[]`. Every event has `qualified_id`, `actor`, `action`, `object`, `actuality`, `event_time` (distinct from article date), `event_time_precision`, `evidence`, `container` (`type`: study|law|product|project|policy|other|null; `name`, `identifier`, `evidence`), and `context_signal` (`foreground|background|uncertain` with exact evidence and rationale). Record detailed referenced events, including actor, act, object, time, actuality and evidence; do not invent details.

Each assignment has `news_key`, `primary_event_id`, `part_of[]` (event IDs of parent container-event, with `relation`, `evidence`), `reacts_to[]` (objects `{event_id,position,evidence}`; position is `support|criticism|neutral|mixed|unclear`). A mention is NOT automatically a reaction. Keep `article_published_at` distinct from `event_time`, and explicit unknowns.

The source receives no other sources, corpus gold, or other extracted records. Extract all fields in the SAME LLM call. Additional fields do not imply zero extra tokens; they avoid an additional *request*.

## 2. Pair judge v5 — same request per compared pair
Input: two independent event records and their evidence, no gold. Output `decision` equivalent|distinct|uncertain, `reason`, and `detail_conflicts[]`. When equivalent, list any explicit conflicting claims as `{field,claim_a,claim_b,evidence_a,evidence_b,status}` with status `reported_conflict|unresolved`. Empty array if no documented conflict. Different emphasis or missing information is not contradiction. This is NOT truth adjudication. No extra API request, but potentially more tokens.

## 3. Composer v5 — deterministic, zero LLM calls
- Build equivalence cards using conservative v4 merge policy, never merge explicit distinct pairs.
- `part_of` creates parent/child card membership within a matrix rooted at the *container event*, without collapsing child cards. Multiple children may refer to one parent.
- `reacts_to` creates directed links from reaction card to target card and retains position per source; no forced merger.
- `context_signal=background` cannot on its own anchor a matrix, and is not sufficient for membership.
- Card-level conflicts from equivalent-event pair judgements are recorded with pair/evidence provenance, never silently resolved.
- No inference of parentage from matching topical words; parent identifiers must be explicit and traceable.
- Article date is never substituted for event date. Unknown references are preserved as unresolved, not invented.
- An isolated population-trend story stays outside a matrix about a specific study unless a grounded `part_of` or `reacts_to` relation explicitly connects it; mere thematic similarity does not.

## 4. Monarch two-source smoke pilot (not yet run)
Use the frozen two monarch sources S473/S474, not an invented reconstruction. Expected structural outcome: **three study-detail cards under the same study matrix; population decline outside**. First inspect actual source content and labels; validate extracted parent identifiers, `part_of`, background/foreground, reaction positions, and date separation. This is a functionality check, not a precision/recall measurement.

## 5. AI gold and costs
Before running on the AI corpus, freeze independently reviewed matrices/cards, `part_of` and reaction positions, with evidence spans, source URLs and explicit abstentions. Track per-source extraction input/output tokens and spend; per-pair judge calls, tokens and spend; composition costs zero. Report retrieval coverage and false merges separately. No gold in prompts.
