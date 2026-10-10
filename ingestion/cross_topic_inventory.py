"""Offline cross-topic source inventory. No new feed is enabled or fetched.

The pilot registry, Italian candidates, and adapter capabilities are kept
separate to avoid claiming candidate endpoints have been verified.
"""
import json
from collections import Counter
from pathlib import Path

from .source_inventory import inventory


def cross_topic_inventory(root):
    root = Path(root)
    pilot = inventory(root)
    candidates = json.loads((root / "config/italian-cross-disciplinary-candidates.json").read_text(encoding="utf-8"))["candidates"]
    rows = []
    for entry in pilot["registry"]:
        rows.append({
            "key": "pilot:" + entry["id"], "name": entry["name"],
            "origin": "ai_models_pilot", "kind": entry["kind"],
            "category": entry["category"], "language": None,
            "site_url": entry["url"], "feed_url": entry["url"] if entry["kind"] == "rss" else None,
            "feed_state": "enabled_unverified" if entry["configured_enabled"] else "disabled_candidate",
            "acquisition_enabled": entry["configured_enabled"],
        })
    for item in candidates:
        rows.append({
            "key": "italian:" + item["id"], "name": item["name"],
            "origin": "italian_candidate", "kind": item["type"],
            "category": item.get("category"), "language": item.get("language"),
            "site_url": item["url"], "feed_url": item.get("suggested_feed"),
            "feed_state": "candidate_unverified",
            "acquisition_enabled": False,
        })
    counts = Counter(x["origin"] for x in rows)
    return {
        "schema_version": 1,
        "purpose": "cross_topic_candidate_inventory_not_an_editorial_whitelist",
        "sources": rows, "total_entries": len(rows),
        "counts_by_origin": dict(sorted(counts.items())),
        "capabilities": pilot["providers"],
        "unrepresented_channels": [
            "general_news_publisher_registry", "reddit_api", "youtube_channel_feeds",
            "youtube_transcripts", "broad_at_protocol_stream",
            "global_mastodon_network", "systematic_sitemaps",
        ],
        "caveats": [
            "An Italian candidate is never auto-enabled.",
            "No claim that all historically discussed sources are present.",
            "No URL is probed or fetched by this report.",
            "Adapter implementation is not the same as live acquisition coverage.",
        ],
    }
