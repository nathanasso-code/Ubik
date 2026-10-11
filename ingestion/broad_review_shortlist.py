"""Generous human review shortlist, preserving uncertain items separately.

This is a routing view, never an editorial deletion from the full archive.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

def select(catalog, limit=300):
    items = catalog["items"]
    ai = [r for r in items if r["relevance_hint"] == "explicit_ai_signal"]
    # Round-robin by original feed to avoid dominance of large academic/general feeds.
    buckets = defaultdict(list)
    for r in ai:
        buckets[(r.get("source_ids") or ["unknown"])[0]].append(r)
    chosen = []
    while len(chosen) < limit and any(buckets.values()):
        for source in sorted(buckets):
            if buckets[source] and len(chosen) < limit:
                chosen.append(buckets[source].pop(0))
    return {"schema_version": 1, "selection_basis": "explicit AI term in feed title or description, source-balanced; no quality or importance exclusion",
            "review_limit": limit, "eligible": len(ai), "selected": len(chosen),
            "not_shown_but_retained": len(items)-len(chosen),
            "items": chosen}

def write_csv(report, output):
    fields = ["title", "authors", "publisher", "source_ids", "published_raw",
              "url", "description", "area_ids", "relevance_hint"]
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in report["items"]:
            writer.writerow({k: ", ".join(row.get(k, [])) if isinstance(row.get(k), list)
                             else row.get(k, "") for k in fields})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=300)
    args = parser.parse_args()
    report = select(json.loads(args.catalog.read_text(encoding="utf-8")), limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(report, args.output)
    print(json.dumps({k: report[k] for k in ("eligible", "selected", "not_shown_but_retained")}))

if __name__ == "__main__":
    main()
