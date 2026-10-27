Ukraine v5 non-regression preregistration

Run after reviewing frozen monarch rejudge 40421847220. Preserve v4 corpus and original gold unchanged. Re-extract each Ukraine source independently using v5, then E5-small top-5 candidate retrieval, four-way judge (equivalent, distinct, uncertain, part_of with direction), and conservative composition. No gold in prompts.

Hard checks: executive order one identity group with four source records; zero diesel-agreement/executive-order merges; no deterioration relative to v4 identity decisions; separate truce acts and reactions. Reader-facing matrix requires at least two independent origins, not merely two publications.

Additional checks: senator and Zelenskyy criticism reactions, Dmitriev support reaction only when supported by original evidence (no position-field scoring); diesel referenced-event identity evaluated without forced agreement; single-source fragments retained without matrix status; no context-only incident merge. Report missing evidence as unknown.

Measure candidate recall before judgment, including role-disagreement misses; preserve one event per source per identity group and permanent distinct veto. Report all calls, tokens, costs, pair judgments, conflicts and provenance. Do not tune rules on Ukraine gold; correct only documented implementation bugs.

## Addendum before Ukraine v5
- Freeze expected presentation per incident: visible matrix (2+ independent origins), candidate incident (coherent but not eligible for visible matrix), single source (one origin even if republished). Report missing gold labels, never infer them from v5 output.
- Reuse existing Sonnet v4 outputs, do not rerun v4. Use the same exact model and configuration for v5 extraction and v5 judge; record any remaining v4/v5 model confound.
- No reaction position metric: v5 has no such field. Evaluate only recorded reaction target and mention/reaction distinctions.
- Test whether one cross-source part_of bridge connects diesel agreement and US executive order; distinguish distinct-card incident merger (weight 1 if adjacent) from card identity merger (weight 3), and unrelated incident bridge (weight 3).
- Measure complete per-source v5 cost (extraction plus attributed judging) against comparable v4 per-source cost; missing baseline means 2x gate unproven.
- Display each part_of edge once, retaining all origins; remove transitive child-to-ancestor edges only in presentation, never from evidence graph. Republished sources count as one independent origin.
- Without summaries, score the strict error-weight column; mark contradiction/position sentence coverage as not evaluated.

## Model audit before any Ukraine calls
- Verified in repository workflow: monarch schema-rejudge explicitly sets UBIK_LLM_MODEL=deepseek/deepseek-v3.2; monarch schema extraction uses the same default in ingestion/ubik_monarch_v5_pilot.py unless overridden by workflow. Confirm exact extraction workflow env and the returned model metadata when available. The observed low cost is consistent with DeepSeek, not evidence of Sonnet.
- V4 Sonnet 5.5 for both stages is a working hypothesis until checked against the frozen run artifacts/configuration; do not label verified prematurely. The comparison is full v5 procedure vs full v4 procedure at the same model, NOT isolated schema change.
- Before setting presentation gold, run a deterministic near-duplicate/shared-origin scan on Ukraine source texts, explicitly including S188 n0 vs S383 n15; preserve raw similarity, shared excerpts and origin assignments, and avoid treating identical headlines alone as proof of common agency.
- Price comparison uses same model, and reports total pipeline cost per source and judge cost per pair separately. An optional cheap-model run is a distinct later experiment.

## Verified v4 baseline (artifact 12591716174, run 40174092045)
- V4 Sonnet 5.5 extraction artifact has model `anthropic/claude-sonnet-5.5`, 9 source records, no per-source errors, and titles plus summaries as inputs; workflow run overall failed in its separate DeepSeek matrix leg, so Sonnet success must be assessed from its artifact, not overall run status.
- The archived v4 artifact alone does NOT verify that its pair judge also ran Sonnet 5.5, nor does it provide original article text or per-call cost. These require separate evidence before a claimed matched-model end-to-end comparison.
- Identical or similar generated titles/summaries cannot establish independent origin. The source-identity scan on this frozen input is a *screen*, not the requested original-excerpt provenance check. Mark uncertain pairs unknown until original excerpts are retrieved.

## Locked two-composer comparison and fail-closed model audit
- PRIMARY: frozen v4 extraction+judge+legacy composer versus v5 extraction+judge+connected-component composer, both Sonnet 5.5. Score incidents as end-to-end procedure outcomes; do not attribute changes exclusively to extraction.
- SECONDARY zero-LLM: pass frozen v4 extraction+judge outputs through v5 composer with an explicit lossless field adapter. If required part_of/identity evidence is missing, record not comparable rather than synthesize edges. This isolates compositional differences only where input equivalence is defensible.
- All new v5 extraction and judgment calls MUST request exact `anthropic/claude-sonnet-5.5`; save requested model and provider-returned model in every call record. Abort on missing/mismatched model field; never silently fall back to DeepSeek. Include model ID and pricing/cost per call in artifact.
- Executive-order B is expected visible matrix even if S188/S383 collapse to one shared origin, provided the other two origins are verified. Record provenance uncertainty explicitly.
- No v5 calls until fixed v4 judge output and source input are identified and replay adapter is validated; otherwise report missing comparability instead of fabricating a baseline.

## FINAL PRE-CALL FREEZE — 2026-10-27 (UTC)
This section is authoritative for the Ukraine run and supersedes the secondary-comparison warning above. No Sonnet v5 Ukraine call had been started at this freeze.
**Error weights (strict, no summaries):** false fact identity merge 3; position/rebuttal merged 3; unrelated incident merger 3; wrong reaction target 2; incident split 2; fact split 1; reaction/mention confusion 1; thematic expansion merged 1; neighboring incidents merged but distinct cards 1. When summaries are available use the two-column table frozen in docs/v5-schema-freeze-and-rollback-preregistered.md. No new weight can be invented post hoc. No increase in weight-3 errors; combined Ukraine+AI weighted totals and existing AI quantitative gate decide promotion, v4 rollback otherwise.
**Cost limit:** total v5 USD per source <= 2.0 x comparable Sonnet v4 USD per source (extraction + attributed judge calls); also report USD per judged pair, total tokens, number of calls and missing prices. If v4 cost cannot be reconstructed, mark the cost gate NOT VERIFIED, not passed.
**Expected presentation (provisional gold before v5):** B US executive order = VISIBLE MATRIX (four reported publications, at least three presumed independent origins even if S188/n0 and S383/n15 are duplicates). Origin independence of S188/S383 remains UNVERIFIED pending original excerpts; this uncertainty does not change B's expected visible status conditional on the other two being independent. For every other incident, expected label is PROVISIONAL / UNADJUDICATED pending independent-origin evidence, not an automatic visible matrix. Categories: VISIBLE MATRIX (>=2 independent origins), CANDIDATE INCIDENT (coherent incident, visibility bar not met), SINGLE SOURCE (one origin, including republished copies). Record expected/predicted and uncertainty per incident; never score unknown gold as correct or incorrect.
**Three outcomes scored separately:** fact/card identity, incident membership/merger, reader presentation; no reaction-position metric.
**Primary comparison:** v4 extraction + v4 judge + legacy composer versus v5 extraction + v5 four-way judge + connected-component composer; procedure-level difference, not schema-only attribution.
**Secondary zero-cost comparison:** feed frozen v4 identities and reacts_to links into a deterministic v5-compatible composition view WITHOUT inventing part_of. The resulting difference from primary v5 includes both part_of and fourth-verdict effects plus extraction differences; do not claim a clean causal isolation of any single factor. Explicitly show missing part_of as absent, not an error or uncomparable condition. Reuse v4 data exactly.
**Model:** fail closed on exact requested and returned `anthropic/claude-sonnet-5.5` for every v5 extraction and judge call; persist per-call model/usage/cost. No model substitution or fallback.
**Special incident bridge:** A diesel agreement versus B executive order: merging distinct cards in adjacent incident = 1; false fact identity merger = 3; unrelated incident merger = 3. Report actual edges responsible.
**Input provenance:** title/summary overlaps are generated-text indicators only; original evidence absent means shared origin is unknown. Preserve provisional origin status and do not treat multiple copies as independent confirmations.
