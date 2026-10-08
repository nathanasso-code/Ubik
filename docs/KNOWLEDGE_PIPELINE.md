# Knowledge pipeline — experimental architecture v0

Status: **experimental contracts**, not an operating ingestion or moderation service. This document records reversible decisions; no automatic truth validation is implemented.

## Separation of concerns

1. **Source**: externally published material or a future native contribution. Store stable ID, canonical URL, publication metadata, original provenance and topic associations. A primary source is a *role relative to a claim*, not a truth certificate; the current `primary` field is a temporary presentation hint.
2. **Informational cluster**: provisional, re-computable grouping of multiple sources describing substantially the same occurrence. The cluster is not a durable debate identifier. Keep membership and merge/split history in future storage.
3. **Epistemic card**: UI projection of a cluster or original primary document. It is not a separate truth-bearing object.
4. **Nucleus**: persistent question or event with its own ID and scope, linked to one or more clusters. It can be created by proposal, automatically suggested, then reviewed and published.
5. **Debate space**: opt-in capability on a published nucleus, never created automatically for every cluster.
6. **Claim and evidence**: future fine-grained validation and source-dependency graph; neither a source nor a cluster is implicitly verified.

## Lifecycle

Cluster: provisional; future algorithms may regroup it. Nucleus: candidate -> reviewed -> published -> archived (archived may be republished). Debate: disabled by default, separately enabled only on published nuclei. These are contract guards, **not authorization**; server-side identity, moderation, review permissions, audit logs and race handling remain to be built.

## Acquisition plan

Start with a bounded AI-models pilot across RSS/Atom, official APIs, research metadata, independent journalism and selected social sources. Persist the original metadata and retrieval timestamps; distinguish publication time from fetch time. Deduplicate exact URL/document identifiers before similarity-based event clustering. Never assume a syndicated article represents independent confirmation. Respect terms, robots/access restrictions, copyright, rate limits and paywalls. Reuse a single ingested document across multiple topics.

Use a deterministic low-cost pass first; run LLM clustering arbitration and summaries selectively, with evidence links and versioning. Topic activity should adjust polling budgets, not demand uniform minute-by-minute polling.

## Promotion to nucleus

Propose nuclei based on *distinct information lines*, repeated clusters over time, topical importance and meaningful differences in evidence. Popularity alone must not promote a nucleus. Search for existing overlapping nuclei before proposing a new one. Explain why a nucleus was proposed. Human editorial correction and community proposal are compatible with automation; human approval of every proposal must not be required at scale.

## Pilot acceptance criteria

- Sources are traceable and never silently discarded by clustering.
- Same-story syndication does not inflate independent evidence.
- Distinct events with similar wording do not merge.
- A new source can update an existing cluster or nucleus without creating a duplicate debate.
- Nuclei retain stable identity when clustering changes.
- No automatic source validation badge or debate activation.
- Audit costs, false merges, missed merges and unnecessary nuclei.

## Out of scope for v0

Real fetching, persistence, clustering inference, LLM synthesis, contributor profiles, comment threads, human review UI, automated publication and production deployment.
