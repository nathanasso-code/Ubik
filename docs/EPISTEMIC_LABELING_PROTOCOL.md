# Epistemic evaluation: labeling protocol v1

This protocol applies to the experimental AI-models RSS corpus. It is not a publication policy.

## Units of comparison

1. **Same document:** two observations resolve to the same canonical original URL. This supports URL-level deduplication only. Multiple feeds linking the same document do not constitute independent corroboration.
2. **Same event:** two **distinct documents** describe substantially the same bounded occurrence, e.g., the same dated product release, published research result, or announcement. Different authors or publishers alone do not establish independence.
3. **Different event:** distinct developments, distinct research papers, separate releases, or educational materials merely sharing a topic.
4. **Uncertain:** insufficient content, unclear event boundaries, missing original source, or ambiguous publication dates. Exclude from scoring.

## Required review evidence

For each same-event label record both original URLs, the precise common occurrence, publication/event dates when available, an evidence excerpt or location for each source, and whether either item syndicates or cites the other. Record reviewer and review date. Distinguish first-party announcements from secondary commentary. A title-only comparison is provisional, never gold.

For negative labels record the **specific distinction**, not merely a low title-similarity score. Include hard negatives with nearly identical titles but different publications or events. Record uncertain pairs separately.

## Dataset design and leakage prevention

Use the full RSS archive for candidate discovery, not only a source-balanced sample. Include positive pairs, hard negatives, and unrelated controls. Keep source-URL duplicates in a separate document-identity set. Do not use a document-identity pair as an event-level positive.

Avoid evaluating a threshold on the same examples used to tune it. Partition by event/document family and time window, not random pairs sharing an article, so the same event cannot leak into train and test. Report event-level precision and recall with denominators, and separately document deduplication accuracy, unknown cases, cross-publisher dependence and coverage.

## Promotion criteria

Provisional labels become verified only after reviewing the original content of **both** documents, citing the supporting evidence and confirming scope. Unverified examples must not be used to claim production accuracy or to publish epistemic cards. If there are no verified positive event pairs, recall is not meaningfully evaluated.

## Current limitations

The seed file contains provisional assistant triage, not a gold standard. The full-archive title matcher is a candidate generator, not an event classifier. The source registry covers only an experimental topic and is not a representative news benchmark.
