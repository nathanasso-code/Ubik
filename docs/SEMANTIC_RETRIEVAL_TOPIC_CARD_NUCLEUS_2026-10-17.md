# Semantic retrieval: topic, card, nucleus — experiment interpretation (2026-10-17)

Canonical definitions: see [UBIK_DECISION_RECORD_2026-10-16.md](UBIK_DECISION_RECORD_2026-10-16.md).

- **Topic**: curated broad information domain. Topic fit is NOT same-event identity.
- **Epistemic card**: one news item/development, potentially synthesized from multiple independent original sources. Same-event or same-development evidence is required before proposing a multi-source card.
- **Nucleus**: rare, persistent, scoped issue that may host multiple cards, sources, contributions, and discussion. Do not create a nucleus for every card; a sufficiently focused topic may need none.
- **Source/document**: remains independently retrievable even when associated with a card, topic, or nucleus.

## Measured retrieval pilot
GitHub Actions run [39016497891](https://github.com/nathanasso-code/Ubik/actions/runs/39016497891) completed successfully. It embedded RSS titles and descriptions of 984 documents with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` and produced the 100 highest-scoring cross-domain candidate pairs absent from the TF-IDF top-5000 baseline on the SAME snapshot. This establishes technical retrieval novelty relative to the bounded baseline, **not** improved same-event recall or classification precision.

Examples:
- EU leaders supporting Zelenskyy / Zelensky turning to Europe for backing: potential same development, requires text-based event adjudication.
- AI fears weaponized / public agency in AI: topical or issue relation, not automatically a shared news card.
- Yemen government offensive / Saudi struggle with Houthis: issue-level connection, not automatic same-event merge.
- AI mathematicians editorial / open-world AI research: broad thematic similarity, not a nucleus by default.

## Required next evaluations
1. Independently annotate a frozen candidate sample with **distinct labels**: `same_news_development`, `related_separate_developments`, `same_persistent_issue`, `topic_only`, `unrelated`, `insufficient_evidence`. These labels are evaluation targets, not automatically verified outputs.
2. Assess title+description retrieval against accessible full texts; use source passages and timestamps before event identity decisions.
3. Measure retrieval recall for **card candidates** separately from topic routing and nucleus relationship discovery. Count false merges and missed links; do not collapse them into one accuracy metric.
4. Preserve original URLs and independent-origin checks; abstain when evidence is insufficient.
5. Keep model-assisted external-web discovery as a separate future experiment with verifiable URLs and bounded costs.

No public cards, nuclei or topic assignments were created by this pilot.
