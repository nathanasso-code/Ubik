"""Offline audit of unselected federated acquisition snapshots.

Counts document observations, not independently corroborated events.
"""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _parse_date(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def audit(federated, *, now=None):
    if not isinstance(federated, dict) or not isinstance(federated.get("observations"), list):
        raise ValueError("Expected federated observations")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Expected timezone-aware clock")
    observations = federated["observations"]
    connector_counts = Counter()
    source_counts = Counter()
    url_sources = defaultdict(set)
    external_ids = defaultdict(set)
    freshness = Counter()
    missing = Counter()
    for item in observations:
        connector = item.get("connector") or "unknown"
        source = item.get("source_id") or "unknown"
        connector_counts[connector] += 1
        source_counts[(connector, source)] += 1
        url = item.get("canonical_url_hint") or item.get("url")
        if url:
            url_sources[url].add((connector, source))
        identity = (connector, source)
        external_id = item.get("external_id")
        if external_id:
            external_ids[identity].add(str(external_id))
        else:
            missing["external_id"] += 1
        published = _parse_date(item.get("published_raw"))
        if published is None:
            freshness["unknown_or_unparseable"] += 1
        else:
            hours = (now - published).total_seconds() / 3600
            if hours < 0:
                freshness["future_timestamp"] += 1
            elif hours <= 24:
                freshness["within_24h"] += 1
            elif hours <= 168:
                freshness["within_7d"] += 1
            else:
                freshness["older_than_7d"] += 1
    overlap = Counter()
    for sources in url_sources.values():
        if len(sources) > 1:
            overlap["url_hints_multiple_sources"] += 1
        if len({connector for connector, _ in sources}) > 1:
            overlap["url_hints_multiple_connectors"] += 1
    return {
        "schema_version": 1,
        "scope": "unselected_acquisition_observations",
        "total_observations": len(observations),
        "by_connector": dict(sorted(connector_counts.items())),
        "by_source": [{"connector": connector, "source_id": source, "count": count}
                      for (connector, source), count in sorted(source_counts.items())],
        "unique_external_ids_by_source": [
            {"connector": connector, "source_id": source, "count": len(ids)}
            for (connector, source), ids in sorted(external_ids.items())],
        "distinct_url_hints": len(url_sources),
        "overlap": dict(overlap),
        "freshness": dict(freshness),
        "missing": dict(missing),
        "interpretation": "URL overlap is not evidence of independent reporting; timestamps may describe different provider clocks.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("federated", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(json.loads(args.federated.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
