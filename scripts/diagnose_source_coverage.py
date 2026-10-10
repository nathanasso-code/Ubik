#!/usr/bin/env python3
"""Source-level coverage diagnostics; no source quality or truth ranking."""
import argparse
import json
from pathlib import Path

def diagnose(discovery, relevance=None):
    relevance_by_observation = {(x.get("source_id"), x.get("url")): x.get("relevance_status") for x in (relevance or {}).get("items", [])}
    reports = {r["source_id"]: r for r in discovery.get("source_reports", [])}
    # Multiple feed observations of one URL are not independent confirmations.
    url_sources = {}
    for item in discovery.get("items", []):
        if item.get("url"):
            url_sources.setdefault(item["url"], set()).add(item.get("source_id", "unknown"))
    shared_urls = {url for url, ids in url_sources.items() if len(ids) > 1}
    sources = {}
    for item in discovery.get("items", []):
        sid = item.get("source_id", "unknown")
        row = sources.setdefault(sid, {"source_id": sid, "stored_items": 0, "feed_named": 0, "feed_unspecified": 0,
                                       "feed_descriptions": 0, "shared_url_observations": 0, "likely_ai": 0, "review_context": 0, "unknown": 0})
        row["stored_items"] += 1
        row["shared_url_observations"] += item.get("url") in shared_urls
        row["feed_named" if item.get("authors") else "feed_unspecified"] += 1
        row["feed_descriptions"] += bool(item.get("description"))
        relevance_status = relevance_by_observation.get((sid, item.get("url")), "unknown")
        row[relevance_status if relevance_status in ("likely_ai", "review_context", "unknown") else "unknown"] += 1
    for sid, report in reports.items():
        row = sources.setdefault(sid, {"source_id": sid, "stored_items": 0, "feed_named": 0, "feed_unspecified": 0,
                                       "feed_descriptions": 0, "shared_url_observations": 0, "likely_ai": 0, "review_context": 0, "unknown": 0})
        row["fetch_status"] = report.get("status", "unknown")
        if report.get("error"):
            row["fetch_error"] = report["error"]
    return {"schema_version": 1, "purpose": "coverage_only_not_quality_ranking", "shared_urls_across_sources": len(shared_urls), "sources": sorted(sources.values(), key=lambda r: r["source_id"])}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("discovery", type=Path)
    p.add_argument("relevance", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    discovery = json.loads(args.discovery.read_text(encoding="utf-8"))
    relevance = json.loads(args.relevance.read_text(encoding="utf-8")) if args.relevance.exists() else None
    result = diagnose(discovery, relevance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Source diagnostics:", len(result["sources"]))
