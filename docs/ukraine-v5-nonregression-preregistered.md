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
