# Ubik — architecture and repository status (2026-10-13)

> **Aggiornamento 18 ottobre 2026:** per il benchmark corrente, le criticità emerse e il nuovo esperimento Qwen con fingerprint per fonte, consultare [HANDOFF_UBIK_2026-10-18.md](HANDOFF_UBIK_2026-10-18.md). Le pipeline sperimentali non equivalgono a produzione.

**Canonical entry point.** This file supersedes the *navigation instructions* of older dated pilot notes; historical results and evidence remain in Git history and docs. Branch: `develop/ubik-core`. `main` is production and is untouched.

## Product invariant: few curated topics, many discovery signals

Hashtags, documents, observations and candidate events are NOT sections. Only existing `data/catalog.json` topics may receive review-only semantic proposals. New topics require explicit editorial decision based on durable importance, gap against existing topics and ability to sustain moderation. Never create a topic per hashtag or story.

## Active research pipeline (offline and manually triggered)

1. **Publisher discovery:** `ingestion/global_rss_pilot.py`, `config/source-registry.global-pilot.json`; bounded global RSS snapshots.
2. **Term and event discovery:** `ingestion/global_discovery.py` and `ingestion/global_event_pairs.py`; term candidates and conservative pair proposals, not verified events.
3. **Social expansion:** `ingestion/global_social_followup.py` queries Bluesky and Mastodon from observed publisher terms. Query drift is a known problem. Shared URLs are *discovery*, not corroboration.
4. **Cross-channel provenance:** `ingestion/hybrid_document_links.py` preserves publisher and social URL/post origins; no implicit trust.
5. **Topic routing:** `ingestion/semantic_topic_router.py` optional multilingual E5 embedding model; fixed topic catalog, conservative margin/threshold, explicit abstention, review-only. `ingestion/hashtag_topic_routing.py` is a lexical contextual **baseline**, not deep semantics.
6. **Review cards:** `ingestion/global_cards.py` emits source-title cards and possible same-event pairs with original links, never synthesized or verified claims.

**Workflows:** `global-discovery-pilot.yml` is a bounded integration pilot; `semantic-topic-routing-pilot.yml` is manual opt-in with heavyweight model dependencies; `core-checks.yml` provides offline regression coverage. Other workflows support historical or separate acquisition experiments, and are **not production schedulers**.

## Legacy/experimental, not canonical production

- `ingestion/topic_* `: topic-seeded discovery pilots, comparison baselines, editorial worksheets; do not treat as the global acquisition entry point.
- `ingestion/ai_issue_review.py`, `ingestion/six_stage_pilot.py`, `ingestion/broad_*`: research prototypes and evidence audits, not automatic news selection.
- `scripts/discover_ai_sources.py` is an older feed parser used by the new global RSS collector. Refactor it behind a shared feed adapter *after* contract tests, not by deleting it blindly.
- `docs/HANDOFF_UBIK_2026-10-12.md`, `docs/START_HERE_UBIK.md` and dated pilot reports: historical continuity, not current operating instructions.

## Hard boundaries and technical debt

- `ingestion/README.md` defines provider-facing observation contracts; selection/routing modules inside `ingestion/` are a **known layering violation** and should eventually move into `discovery/` or `selection/` after import/test migration.
- Social discovery is still based on short, often broad terms; a phrase/entity extraction stage and language-aware evaluation are needed.
- URL-hint equivalence does not prove same canonical article; cross-publisher host count does not prove independent reporting.
- The E5 model workflow exists but its live inference has not been confirmed. Cosine thresholds are uncalibrated.
- Pilot artifact snapshots expire; no persistent cross-run ledger, automatic production publication or scheduled full acquisition is active.
- `api/feed.js` still uses its existing storage integration; do not pretend pilot output is deployed.
- No historical experiment should be deleted until its imports, CI references, reproducibility, and rollback impact are checked.

## Evidence and maintenance

- Current detailed handoff: `docs/HANDOFF_UBIK_2026-10-13.md`.
- Global-first decisions and results: `docs/GLOBAL_DISCOVERY_ARCHITECTURE_2026-10-13.md`.
- Core UI contracts: `docs/CORE_ARCHITECTURE.md`.
- Latest runs: https://github.com/nathanasso-code/Ubik/actions
- CI: `python -m unittest discover -s tests -p 'test_*.py'` and `Ubik Core checks`.

## Cleanup audit, phase 1

Git branches inspected: **only `main` and `develop/ubik-core`**, no stale branches to delete. No pull requests found. Avoid deleting the production branch or the active development branch.

Current policy: **archive logically before physical deletion**. Preserve historical pilot notes and regression tests until references and usefulness are audited. First cleanup is a canonical architecture map and navigation update; destructive pruning must be backed by a manifest, import graph, CI and a reversible commit.


## Semantic evaluation update — 13 October

Live multilingual E5 runs succeeded technically: `38319834727` evaluated 80 eligible hashtags and abstained on all 80; `38319904689` evaluated 79 and abstained on all 79. These outcomes show conservative gating, **not** measured routing quality; threshold calibration and negative controls are pending.

New `ingestion/blind_semantic_neighbors.py` with `tests/test_blind_semantic_neighbors.py` extends the global pilot: multilingual title embeddings find cross-publisher nearest neighbors **without topic names or datacenter terms**. The semantic job uses the exact frozen RSS artifact from the discovery job, alongside hashtag-topic routing, and retains candidate URL/title evidence. Similarity is not corroboration, causal linkage, contradiction, or same-event identity. Run `38320346965` must be inspected before reporting findings.

Next refactor: move discovery and review logic behind separate packages with compatibility wrappers only after current pipeline and tests are stable; prioritize annotated semantic precision and blind held-out evaluation before deleting historical experiments.


## Epistemic review gate — mandatory reading for handoff

Read `docs/EPISTEMIC_REVIEW_CONTRACT.md` before editing or displaying epistemic relations. A semantic neighbor is **not** a verified claim. `ingestion/epistemic_evidence_gate.py` is a source-text/quote/hash consistency and editorial-review eligibility gate; it does not fetch documents, validate facts, establish publisher independence or authorize public publication. Tests: `tests/test_epistemic_evidence_gate.py`. Never silently promote its output to `verified` or `published`. Full-article collection and actual claim-level annotations are the next implementation boundary.

Recent run `38320735744` completed successfully: 324 RSS hints, 1,256 semantic pairs, 60 diverse manual review items, 80 eligible hashtag groups and zero topic proposals. The older **frozen** datacenter benchmark is documented against `38320346965`; do not conflate the two run snapshots.


## Nota di continuità — 16 ottobre 2026

La descrizione tecnica precedente resta storicamente utile, ma le **decisioni di prodotto e i test OpenRouter più recenti** sono in [UBIK_DECISION_RECORD_2026-10-16.md](UBIK_DECISION_RECORD_2026-10-16.md). In particolare: feed generale per fonti fuori topic; tag distinti dai topic; card per singole notizie multi-fonte; nuclei più rari e orientati a questioni persistenti e concentrazione della comunità. Workflow OpenRouter sperimentale presente su `main`, mentre il ramo di sviluppo resta `develop/ubik-core`; nessuna inferenza di deploy pubblico.
