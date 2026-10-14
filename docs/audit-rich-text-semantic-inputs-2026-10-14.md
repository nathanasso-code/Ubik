# Audit: substantial texts were acquired but not used in core semantic experiments

Verified on 2026-10-14 in `develop/ubik-core`.

## What the code proves
- `ingestion/europe_pmc_licensed_texts.py` downloads Europe PMC fullTextXML and stores bodies for explicitly recognized open licenses, in `data/discovery/licensed-papers/*.json`.
- `ingestion/semantic_topic_neighbor_pilot.py::extract` **discards the body** and retains only title and description (max 900 chars). E5 embeddings are calculated from those fields.
- `ingestion/statement_relation_pilot.py::claims` extracts candidates only from title and description; directional NLI therefore does not see article bodies.
- `ingestion/hybrid_event_review.py` reuses the title/description embedding baseline.
- Thus prior rich-text acquisition cannot validate the semantic pipeline's performance on substantial text.

## Recovery work
Added `ingestion/rich_text_corpus.py` and a CI artifact `data/discovery/rich-text-corpus.json`. It collects previously retained Europe PMC licensed bodies (minimum 2,000 chars), keeps URL/license/source provenance, records original length and explicit truncation at 30,000 chars, and rejects short or unlicensed/missing-provenance records.

This is **a separate rich-text corpus**, not yet wired into the E5/NLI benchmark. No assertion of improved semantic accuracy is justified yet. Next experiment must compare the **same documents** under title/abstract versus full-text chunk retrieval + claim-level NLI and category assignment, with independently reviewed labels.

## Historical figures (from previous experiment reports; not newly measured)
Prior reports recorded 9 licensed Europe PMC bodies (about 454,475 characters) and 100+ substantial journalistic pages temporarily parsed. Journalistic full texts were not persistently fed to NLI. These counts require confirmation against current CI artifacts.

## Why this matters
The correct comparison is data sufficiency **and** model capability. We should not attribute poor NLI and categorization results solely to models when the upstream input excluded the richer content that had already been acquired.
