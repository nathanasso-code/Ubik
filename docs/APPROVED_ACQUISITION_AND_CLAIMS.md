# Ubik — approved acquisition and claim comparison, October 13 2026

## Implemented and connected (development branch only)

**Acquisition:** `ingestion/approved_https_fetch.py` provides an opt-in single-document HTTPS fetcher. Requires explicit approved-host allowlist, operator-confirmed rights and robots review; retrieves and checks robots.txt, rejects disallowed paths, redirects, non-200 responses, unexpected content types, oversized bodies, private/non-global DNS answers, credentials, non-HTTPS URLs and nonstandard ports. Uses direct TLS with certificate hostname validation and **IP pinning** for each request; no cookies, proxy, authentication, paywall bypass or redirect following. `ingestion/approved_claim_pipeline.py` chains approved fetch -> `authorized_source_text.py` -> hash-grounded `source_claim_candidates.py`.

**Claim candidates:** `source_claim_candidates.py` extracts verbatim candidate sentences from hash-consistent source texts. These are *not* independently verified factual claims; segmentation is heuristic and multilingual handling incomplete.

**Cross-source comparison:** `source_claim_comparisons.py` assembles review worksheets only when both source texts and candidate passages are available. It does **not** infer contradiction, agreement or causation. It defaults to `insufficient_evidence` and requires explicit editorial comparison and `epistemic_evidence_gate.py` before a label can even be considered for review.

**Card previews:** `semantic_discovery_cards.py` renders unverified source-linked semantic neighbors from the global RSS experiment. It does **not** imply source-body retrieval. A card based on compared source claims cannot be considered epistemically reviewed until real approved source texts are available and an editor assesses the claims.

## Strict operational boundary

**No publisher is preapproved.** An operator must assess each publisher's terms and source permissions and explicitly supply a policy file. The GitHub global pilot does **not** auto-fetch article bodies; it only runs the safe transport's mocked tests and continues RSS/title-based discovery. This is deliberate: robots.txt permission is not a copyright license (RFC 9309). Do not add blanket `rights_confirmed=true` to bypass this requirement.

The new transport is a **minimal research adapter**, not a production-hardened crawler. Further hardening required before unattended operation: explicit egress firewall, content decompression controls, `Retry-After`, per-host budgets and caching, IPv6/IDNA edge cases, robots HTTP-status handling, anti-abuse monitoring, and rights/retention audit. HTML extraction is heuristic, and quote hashes prove local integrity only.

## Usage after publisher approval

```json
{
  "approved_hosts": ["approved-publisher.example"],
  "rights_confirmed": true,
  "robots_review_confirmed": true
}
```

```bash
python -m ingestion.approved_claim_pipeline --url https://approved-publisher.example/article --policy /secure/approved-policy.json --output /secure/article-claims.json
```

The policy is an **operator assertion**, not automatically verified legal permission. Avoid committing full publisher text or policies with private data to public GitHub artifacts.

## Test and evaluation protocol

- `tests/test_approved_https_fetch.py`: mocked DNS/private address, rights, robots and HTTPS allowlist tests.
- `tests/test_approved_claim_pipeline.py`: acquisition-to-candidates integration with synthetic HTML.
- `tests/test_source_claim_pipeline.py`: two synthetic sources, exact source quotes, review worksheet and fail-closed hash checks.
- `tests/test_epistemic_evidence_gate.py`: verbatim quote and provenance gate.

The next required empirical step is to secure authorized article-body access to **at least two independent publishers**, run the above pipeline, compare specific claims with a reviewer and evaluate a diverse sample of candidate pairs. No real-body precision estimate exists yet. Do not describe the current semantic card previews as validated epistemic cards.

## Handoff links

- `docs/ARCHITECTURE_CURRENT.md`: canonical architecture.
- `docs/EPISTEMIC_REVIEW_CONTRACT.md`: editorial validation schema.
- `docs/BLIND_SEMANTIC_RESULT_2026-10-13.md`: frozen Yandex datacenter benchmark and false positives.
- `docs/HANDOFF_UBIK_2026-10-13.md`: chronological handoff.
- Workflow `.github/workflows/global-discovery-pilot.yml` generates RSS semantic preview artifacts and runs the safe-claim pipeline tests; it does not fetch full articles.
