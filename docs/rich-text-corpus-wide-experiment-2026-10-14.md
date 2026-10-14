# Audit and first diagnostic: rich texts across the entire existing corpus

Date: 2026-10-14. Source: GitHub Actions run 38549804695, artifact 11886551627. Branch: `develop/ubik-core`.

## Verified, not inferred
- Persistent corpus: **4,168 distinct records**.
- **178 distinct records** have at least one access-test result indicating substantial article text or long abstract (these are *access signals*, not stored article bodies).
- Public-text extraction attempted **150 pages**: **94** yielded at least 2,000 characters. **Zero** full texts were persisted in this artifact; they were processed in memory.
- Nine licensed Europe PMC full texts were persisted; total raw text length **464,867 characters**. This is a domain-specific corpus, not a news-event cluster.
- Four Wikinews pages were marked as substantial but processed in memory, not persisted.
- Earlier workflow recorded 332 substantial-article access-test outcomes, 110 substantial-page outcomes and 17 long-abstract outcomes; these are repeated tests, not unique articles.

## Actual diagnostic performed locally on the retained papers
36 paper pairs were evaluated with an unweighted bag-of-words cosine, comparing titles against entire bodies. Median title similarity **0.0581**; median full-body similarity **0.7913**. This striking increase is **not evidence of improved relevance**: generic scientific vocabulary and boilerplate inflate whole-document similarity. This is a negative finding against naively embedding/comparing entire bodies.

## Reproducible GitHub implementation
- `ingestion/rich_access_audit.py` inventories **all** rich-access candidates from the persistent corpus.
- `ingestion/rich_text_corpus.py` reconstructs the stored licensed bodies.
- `ingestion/rich_text_similarity_diagnostic.py` compares titles and bodies (lexical diagnostic only).
- CI workflow now produces `rich-access-audit.json`, `rich-text-corpus.json`, and `rich-text-similarity-diagnostic.json` after the required input steps.

## Unresolved requirement and next work
The requested **news cluster with substantial original text** does not yet exist as a persisted artifact: access signals and text-length metadata cannot substitute for article bodies. Recover legally accessible bodies for the 178 candidates, persist only under appropriate permissions, and use short relevant chunks for E5 and claim-level NLI. Compare title/abstract versus chunk-rich inputs on **the same news pairs**. Do not claim the existing paper diagnostic measures E5/NLI or event identity.
