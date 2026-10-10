"""Offline duplicate accounting across immutable acquisition snapshots.

Repeated observations remain in the archive. These diagnostics never discard
records or infer that matching links constitute independent corroboration.
"""
from collections import Counter, defaultdict


def duplicate_report(federated):
    observations = federated.get("observations", [])
    if not isinstance(observations, list):
        raise ValueError("Expected federated observations")
    by_identity = defaultdict(set)
    occurrences = Counter()
    by_url = defaultdict(set)
    for item in observations:
        if not isinstance(item, dict):
            continue
        connector, source, external = (item.get("connector"),
                                       item.get("source_id"),
                                       item.get("external_id"))
        snapshot = item.get("snapshot")
        if not all(isinstance(x, str) and x for x in (connector, source, external)):
            continue
        identity = (connector, source, external)
        occurrences[identity] += 1
        if isinstance(snapshot, str):
            by_identity[identity].add(snapshot)
        hint = item.get("canonical_url_hint")
        if isinstance(hint, str) and hint:
            by_url[hint].add(identity)
    repeated = {k: n for k, n in occurrences.items() if n > 1}
    cross_snapshots = {k: n for k, n in repeated.items() if len(by_identity[k]) > 1}
    shared_urls = {url: ids for url, ids in by_url.items() if len(ids) > 1}
    return {
        "schema_version": 1,
        "total_observations": len(observations),
        "observations_with_valid_identity": sum(occurrences.values()),
        "unique_provider_identities": len(occurrences),
        "repeated_provider_identities": len(repeated),
        "extra_repeated_observations": sum(n - 1 for n in repeated.values()),
        "identities_repeated_across_snapshots": len(cross_snapshots),
        "canonical_url_hints_with_multiple_identities": len(shared_urls),
        "selection_applied": False,
        "deduplication_applied": False,
        "caveat": "Same provider identity can be seen repeatedly; shared URLs do not prove independent sources."
    }
