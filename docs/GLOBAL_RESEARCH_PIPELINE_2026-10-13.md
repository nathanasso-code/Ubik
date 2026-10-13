# Global research orchestration — operational contract

The existing `global-discovery-pilot.yml` already runs topic-agnostic RSS discovery, candidate terms, Bluesky/Mastodon follow-up, hybrid links, blind multilingual E5 neighbor retrieval, review queues and fixed-catalog topic proposals. It is a **manual bounded research pilot**, not a persistent global crawler or production feed. Social hashtags are expansion signals, not the exclusive seed or proof.

## Next-stage order and hard gates

1. **Acquire discovery metadata globally** from diverse configured RSS publishers; incorporate GDELT, Crossref, OpenAlex and other already implemented provider adapters as separate bounded observations, without silently pretending they are all connected to this workflow.
2. **Expand** using document links from original Bluesky posts and public Mastodon observations; normalize URLs and preserve each original post/source reference. Mastodon search is instance-dependent and unauthenticated full-text status search may be unavailable.
3. **Deduplicate hints** without asserting canonical identity; measure coverage by language, geographic region, publisher, and observation connector.
4. **Acquire full bodies only where permitted**, record extraction completeness, revision/date, SHA-256, rights, and provenance. On 429/503, honor rate limits and abstain rather than retry aggressively.
5. **Extract specific propositions** with source quotes and actor, predicate, target, event date, place, modality, negation, numeric quantity and reporting-time scope. Preserve uncertain/null values and never call a candidate fact verified.
6. **Select** on novelty, significance, diverse provenance and available evidence; distinguish selection priority from factual credibility.
7. **Compare** candidate propositions: same event, related distinct events, support, contradiction, temporal update, shared context, unrelated, insufficient evidence. A similarity score alone never creates an epistemic edge.
8. **Synthesize** only attributable propositions, separating established observations, disputes and missing evidence. Do not create generic placeholder summaries as if they were information.
9. **Categorize last**, against the existing editorial topic catalog. Abstain where ambiguous; never create topics per hashtag or article.
10. **Evaluate** on frozen random and stratified samples: precision of event merges, false merges, extraction completeness, claim grounding, category accuracy, language/region coverage. No precision/recall assertion before independent labels.

## Immediate empirical bottleneck

The 120 Wikinews-body experiment succeeded, but subsequent rapid reruns hit HTTP 429. The title-only clustering conflated different Caloundra soccer rounds and NYC primary/general elections. Guard tests are implemented, but general event-frame reasoning is not. No end-to-end diverse-publisher, source-body, claim-relation, synthesis and classification run has been validated.

## Runbook

Use the existing GitHub Actions **Global topic-agnostic discovery pilot** manual dispatch on `develop/ubik-core`, inspect both artifacts, then audit sources and claim bodies in a rights-approved separate phase. The GitHub connector in this session can inspect Actions and modify files but cannot dispatch a new workflow; do not claim that a new run occurred. Avoid editing `main` or production storage.
