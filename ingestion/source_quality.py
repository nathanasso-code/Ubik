"""Offline source-level freshness, duplicates and provenance diagnostics.

Expected publication universe is unknown: this deliberately does not compute recall.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone

from .audit import _parse_date


def acquisition_quality(federated, *, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Expected aware now")
    observations = federated.get("observations")
    if not isinstance(observations, list):
        raise ValueError("Expected observations")
    by_source = defaultdict(list)
    for item in observations:
        if not isinstance(item, dict):
            raise ValueError("Invalid observation")
        by_source[(item.get("connector") or "unknown",
                   item.get("source_id") or "unknown")].append(item)
    rows = []
    for (connector, source), items in sorted(by_source.items()):
        identities = Counter(str(x["external_id"]) for x in items
                             if isinstance(x.get("external_id"), str) and x["external_id"])
        fresh = Counter()
        ages = []
        for item in items:
            stamp = _parse_date(item.get("published_raw"))
            if stamp is None:
                fresh["unknown"] += 1
                continue
            age = (now - stamp).total_seconds() / 3600
            if age < 0:
                fresh["future"] += 1
            elif age <= 24:
                fresh["within_24h"] += 1
            elif age <= 168:
                fresh["within_7d"] += 1
            else:
                fresh["older_than_7d"] += 1
            ages.append(age)
        rows.append({
            "connector": connector, "source_id": source,
            "observations": len(items),
            "unique_external_ids": len(identities),
            "duplicate_extra_observations": sum(n - 1 for n in identities.values()),
            "missing_external_ids": len(items) - sum(identities.values()),
            "missing_authors": sum(not (x.get("metadata") or {}).get("authors")
                                   for x in items if isinstance(x.get("metadata"), dict)),
            "freshness": dict(fresh),
            "oldest_age_hours": max(ages) if ages else None,
            "newest_age_hours": min(ages) if ages else None,
            "estimated_recall": None,
            "status": "observed_sample_not_population",
        })
    return {
        "schema_version": 1, "scope": "unselected_source_observations",
        "by_source": rows,
        "total_observations": len(observations),
        "global_recall": None,
        "warnings": [
            "Unknown expected source output prevents recall estimates.",
            "Observed age is not ingestion latency; ingestion timestamps are required.",
            "Missing author metadata is not evidence that an article has no author.",
            "Provider-specific publication and discovery clocks differ.",
            "No source ranking, content selection or epistemic clustering is performed.",
        ],
    }
