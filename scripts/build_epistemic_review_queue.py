#!/usr/bin/env python3
"""Build a reproducible, unlabeled review sample from the RSS discovery archive.

Selection is not clustering, event recognition, truth validation or human labeling.
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def build_queue(discovery, per_source=3, max_total=60):
    if not isinstance(per_source, int) or per_source < 1 or not isinstance(max_total, int) or max_total < 1:
        raise ValueError("Sampling limits must be positive integers")
    by_source = defaultdict(list)
    for item in discovery.get("items", []):
        if not all(isinstance(item.get(k), str) and item[k].strip() for k in ("source_id", "url", "title")):
            continue
        by_source[item["source_id"]].append(item)
    # Stable across input ordering and independent of the repository's cumulative cache order.
    selected = []
    for sid in sorted(by_source):
        ranked = sorted(by_source[sid], key=lambda x: (
            hashlib.sha256((sid + "\0" + x["url"]).encode()).hexdigest(), x["url"]
        ))
        seen_urls = set()
        for item in ranked:
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            selected.append({
                "observation_id": item.get("id") or hashlib.sha256((sid + "\0" + item["url"]).encode()).hexdigest()[:24],
                "source_id": sid,
                "url": item["url"],
                "title": item["title"],
                "description": item.get("description") or "",
                "published_raw": item.get("published_raw"),
                "publisher": item.get("publisher"),
                "authors": item.get("authors", []),
                "review_status": "unreviewed",
                "event_label": None,
                "notes": "",
            })
            if len(seen_urls) >= per_source:
                break
    # Round-robin by source to avoid filling the budget from early alphabetic sources.
    buckets = defaultdict(list)
    for item in selected:
        buckets[item["source_id"]].append(item)
    result = []
    while len(result) < max_total and any(buckets.values()):
        for sid in sorted(buckets):
            if buckets[sid] and len(result) < max_total:
                result.append(buckets[sid].pop(0))
    return {
        "schema_version": 1,
        "purpose": "manual_event_identity_review_not_ground_truth",
        "label_instructions": "Assign the same event_label only when observations describe substantially the same occurrence. Similar topic alone is insufficient. Leave uncertain items unreviewed; never infer independent corroboration from different feeds.",
        "items": result,
        "coverage": {"available_sources": len(by_source), "sampled_sources": len({x["source_id"] for x in result}), "sampled_observations": len(result)},
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("discovery", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--per-source", type=int, default=3)
    p.add_argument("--max-total", type=int, default=60)
    args = p.parse_args()
    discovery = json.loads(args.discovery.read_text(encoding="utf-8"))
    result = build_queue(discovery, args.per_source, args.max_total)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"]))


if __name__ == "__main__":
    main()
