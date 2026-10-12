# Ubik epistemic links — reviewer contract (2026-10-13)

This document is the handoff for **source-grounded claim comparison**. It must be read together with [ARCHITECTURE_CURRENT.md](ARCHITECTURE_CURRENT.md), [BLIND_SEMANTIC_RESULT_2026-10-13.md](BLIND_SEMANTIC_RESULT_2026-10-13.md), and [HANDOFF_UBIK_2026-10-13.md](HANDOFF_UBIK_2026-10-13.md).

## Verified state of the experimental pipeline

- Global publisher snapshot: 324 distinct URL hints in the validated run.
- Blind E5 retrieval: 1,258 cross-host semantic-neighbor pairs on run `38320346965`. Datacenter/Yandex case recovered at ranks 59 and 63; **not** verified as factual reporting or causal relation.
- Balanced queue: 60 unreviewed pairs in successful run `38320735744`, generated without editing the original semantic ranks.
- Hashtag-to-topic E5: 80 eligible, 0 proposals, 80 abstentions in run `38320735744`. The 0 result is a conservative threshold outcome, not proof of model precision.
- Source-body evidence: **not yet collected or assessed in those runs**. No claims may be marked supported or contradicted from headline similarity.

## Separation of responsibilities

1. **Discovery**: RSS, social observations and links; never editorial truth.
2. **Retrieval**: multilingual embeddings suggest document neighbors; no topic seed or held-out example in the retrieval query.
3. **Selection**: bounded review queue preserves source URLs, frozen rank, and avoids overconcentration; not a statistically random quality sample.
4. **Source capture**: store exact accessible source text, retrieval time, original URL, content hash, and source license/access restrictions. No paywall bypass. A shared social URL is not independent reporting.
5. **Claim annotation**: reviewer compares specific propositions, identifying agent, action, target, time, place and scope. Preserve verbatim supporting passages; distinguish same event, related distinct events, shared context, support, contradiction, source-asserted causality, spurious and insufficient evidence.
6. **Gate**: `ingestion/epistemic_evidence_gate.py` checks that review evidence quotes occur verbatim in hashed supplied source texts, both source passages exist for substantive relations, compared claims and rationale are present, and a reviewer is named. It returns `eligible_for_editorial_review`, **not verified truth** and never publication.
7. **Editorial decision**: only a subsequent, separately reviewed and auditable workflow may decide whether a claim relation is reliable enough for display. No automatic new topic, section, claim verification or public publication.

## Review input contract

Example (synthetic, not a real finding):

```json
{
  "relation_type": "contradicts_claim",
  "reviewer_id": "editor-123",
  "left": {"url": "https://example.org/a"},
  "right": {"url": "https://example.net/b"},
  "evidence": [
    {"url": "https://example.org/a", "quote": "Exact verbatim passage from the first article, at least twenty characters."},
    {"url": "https://example.net/b", "quote": "Exact verbatim passage from the second article, at least twenty characters."}
  ],
  "compared_claims": ["First explicitly formulated proposition", "Second explicitly formulated proposition"],
  "rationale": "Explain why the propositions address the same event, entity, scope and timeframe."
}
```

Source mapping passed to the gate:

```json
{
  "https://example.org/a": {"text": "...", "sha256": "sha256 of the exact UTF-8 source text"},
  "https://example.net/b": {"text": "...", "sha256": "sha256 of the exact UTF-8 source text"}
}
```

**Security / epistemic limitations:** Hashes prove only internal text consistency, not source authenticity or truth. A quote can be cherry-picked. A reviewer ID alone is not a signed identity. Cross-host matches may originate from one wire story. The gate does not check temporal scope, negation, evidence quality or source independence; those require separate annotation and verification. User-supplied passages are untrusted. No automatic trust escalation.

## Next autonomous work

- Build a safe, bounded article text acquisition adapter with SSRF protections, robots/access controls, no paywall circumvention and extraction provenance.
- Label a balanced and an independent random sample of document pairs, including false positives and multilingual cases. Measure precision, false merges and missed relations.
- Introduce typed claim/entity/time extraction **only as hypotheses**, with reviewer overrides and provenance.
- Rationalize `ingestion/` into acquisition vs discovery vs review packages via compatibility wrappers and import/tests audit. Do not delete historical modules until dependencies are known.
- Maintain **few editorial topics, many semantic signals**; never convert hashtags into sections.


## Safe source acquisition milestone — offline adapter

`ingestion/authorized_source_text.py` now extracts paragraphs from **externally obtained, explicitly authorized HTML**; it omits common navigation/script blocks, enforces input size, rejects missing/insufficient text and returns a SHA-256 of the exact extracted UTF-8 passage plus original HTTPS URL and extraction metadata. Tests: `tests/test_authorized_source_text.py`. It performs **zero HTTP requests** and must not be described as a live article fetcher. `--authorized` is an explicit operator assertion, not automatic verification of licensing or robots permissions. The extraction is heuristic and does not prove article completeness or source authenticity.

**Security boundary:** Do NOT bolt a plain `urllib.request.urlopen` or `requests.get` onto this function. DNS checks without pinning are vulnerable to rebinding; redirect targets need revalidation, and arbitrary URLs can reach internal resources. Future network acquisition must use a reviewed SSRF-safe transport with resolved-IP pinning, redirect policy, egress allowlisting, rate limits, content-type/size/timeouts, robots and publisher access checks, and no paywall bypass. Until that is in place, authorized HTML must be supplied through a separate controlled acquisition path. A safe offline adapter is a narrower, honest milestone toward claim-level evidence, **not a completed source ingestion system**.

**Integration gap:** the capture adapter returns a URL-keyed mapping with metadata and `text`/`sha256` fields, compatible with `epistemic_evidence_gate.validate`; however, no live source corpus, annotated claims or reviewer decisions have yet been generated.
