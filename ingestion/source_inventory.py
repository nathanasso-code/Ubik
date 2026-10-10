"""Read-only, non-editorial inventory of configured and implemented discovery sources.

A registered feed is not proof that it is reachable. An implemented adapter is
not proof that a given endpoint works. Never conflate these statuses.
"""
import json
from collections import Counter
from pathlib import Path

PROVIDER_IMPLEMENTATIONS = {
    "rss": "scripts/discover_ai_sources.py",
    "hacker_news": "scripts/discover_hacker_news.py",
    "gdelt": "ingestion/gdelt_doc.py",
    "bluesky": "ingestion/public_adapters.py",
    "mastodon": "ingestion/public_adapters.py",
    "openalex": "ingestion/public_adapters.py",
    "crossref": "ingestion/public_adapters.py",
}
LIVE_EVIDENCE = {
    "bluesky": {"status": "bounded_success", "observations": 3},
    "mastodon": {"status": "http_422_unresolved", "observations": 0},
    "openalex": {"status": "bounded_success", "observations": 5},
    "crossref": {"status": "bounded_success", "observations": 4},
}


def inventory(root):
    root = Path(root)
    registry = json.loads((root / "config/source-registry.ai-models.json").read_text(encoding="utf-8"))
    rows = []
    for entry in registry["sources"]:
        enabled = entry.get("enabled") is True
        kind = entry.get("kind", "unknown")
        is_feed = kind == "rss" and bool(entry.get("url"))
        rows.append({
            "id": entry["id"], "name": entry["name"], "kind": kind,
            "category": entry.get("category"), "url": entry.get("url"),
            "configured_enabled": enabled,
            "implementation": "scripts/discover_ai_sources.py" if is_feed else None,
            "readiness": "configured_unverified" if enabled and is_feed else "candidate_not_enabled",
            "reason": entry.get("reason"),
            "scope": "ai-models_pilot_not_global_source_catalog",
        })
    providers = [{
        "provider": name, "implementation": path,
        "implementation_present": (root / path).is_file(),
        "live_evidence": LIVE_EVIDENCE.get(name),
        "coverage_limit": ("single_author_feed_not_firehose" if name == "bluesky" else
                           "selected_instance_local_timeline" if name == "mastodon" else
                           "query_scoped_not_global_firehose" if name == "gdelt" else
                           "bounded_sample_only"),
    } for name, path in PROVIDER_IMPLEMENTATIONS.items()]
    counts = Counter((row["kind"], row["configured_enabled"]) for row in rows)
    return {
        "schema_version": 1,
        "scope": "registered_ai_models_pilot_and_known_adapter_implementations",
        "registry_entries": len(rows),
        "enabled_rss": counts[("rss", True)],
        "registry": rows,
        "providers": providers,
        "caveats": [
            "Not a complete global inventory of all sources ever discussed.",
            "Registration does not imply successful fetching or usable content.",
            "Live evidence is limited to documented one-time October 2026 smoke tests.",
            "No network calls were made by this inventory.",
        ],
    }
