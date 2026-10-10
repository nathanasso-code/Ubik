# Feed, cluster and corroboration: product semantics

## Feed inclusion is not conditional on clustering

Ubik is also a news aggregator. A useful single-source item remains eligible for the feed on its own merits. It must not be discarded or downranked merely because no related article is found. Clustering is an optional **representation and attention-management mechanism**, not an eligibility test.

## What a cluster contributes

A cluster can (1) reduce repeated coverage of a bounded event, (2) draw attention to recurring coverage without claiming that volume equals importance, and (3) provide a concise source-linked synthesis so users can understand the shared news without opening each source. Each original item remains accessible with provenance.

**Multiple coverage is not automatically corroboration.** Independent outlets can quote the same press release, share wire copy, or rely on one original report. Show number of documents, number of publishers and independence of underlying origins as different fields; unknown independence must remain unknown.

## Three independent axes

- **Item significance:** whether a single item deserves attention, regardless of cluster membership.
- **Event grouping:** whether documents refer to the same bounded event. An event cluster can contain one or many documents, but a singleton need not appear as a visually special cluster.
- **Evidence support:** whether claims are independently corroborated, disputed or unassessed. Do not infer this from source count.

Nuclei are persistent higher-level questions or issues, distinct from event clusters. Debate and validation are separate optional processes, not side effects of clustering.

## Implementation constraints

Do not auto-merge articles based on topical similarity alone. Do not create misleading consensus indicators from the number of publishers. Keep single-source news visible in future feed prototypes. Preserve links and source attribution. Do not claim a verified clustering accuracy until a held-out evaluation set with both positives and hard negatives exists.
