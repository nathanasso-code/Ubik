#!/usr/bin/env python3
"""Build a conservative author discovery queue from collected source metadata.

No identity merging, reputation scoring, profile guessing, or publication.
"""
import argparse
import collections
import json
from pathlib import Path

def build_candidates(discovery):
    groups = collections.defaultdict(lambda: {"publications": [], "source_ids": set(), "source_links": set()})
    for item in discovery.get("items", []):
        if not item.get("url"):
            continue
        for author in item.get("authors") or []:
            name = " ".join(str(author).split())
            if not name or "@" in name or len(name) > 160:
                continue
            # Group by exact normalized name only; same name does not prove same person.
            key = name.casefold()
            entry = groups[key]
            entry.setdefault("name", name)
            entry["publications"].append({"title": item.get("title"), "url": item["url"], "publisher": item.get("publisher"), "published_raw": item.get("published_raw")})
            entry["source_ids"].add(item.get("source_id", "unknown"))
            if item.get("discovered_from"):
                entry["source_links"].add(item["discovered_from"])
    result = []
    for key, entry in groups.items():
        result.append({
            "candidate_id": key,
            "display_name": entry["name"],
            "identity_status": "unverified",
            "identity_note": "Matching names are not evidence of a single identity.",
            "source_ids": sorted(entry["source_ids"]),
            "discovered_from": sorted(entry["source_links"]),
            "publication_count": len(entry["publications"]),
            "sample_publications": entry["publications"][:5],
            "suggested_next_step": "Check author-supplied profile or publication byline; discover an official personal feed before subscribing."
        })
    return {
        "schema_version": 1,
        "topic_id": discovery.get("topic_id"),
        "generated_from": "discovery-metadata",
        "candidate_count": len(result),
        "candidates": sorted(result, key=lambda x: (-x["publication_count"], x["display_name"].casefold()))
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = build_candidates(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Author candidates: {data['candidate_count']}")
