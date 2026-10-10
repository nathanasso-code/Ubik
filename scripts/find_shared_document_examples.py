#!/usr/bin/env python3
"""Collect same-URL observations across distinct feeds for provenance review.

Identical canonical URLs establish shared document identity, NOT independent reporting
or same-event evidence for two different articles.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def same_document_examples(discovery, limit=50):
    if type(limit) is not int or limit < 1:
        raise ValueError("Positive limit required")
    by_url = defaultdict(dict)
    for item in sorted(discovery.get("items", []), key=lambda x: (x.get("source_id", ""), x.get("url", ""), x.get("id", ""))):
        if item.get("url") and item.get("source_id") and item.get("title"):
            by_url[item["url"]].setdefault(item["source_id"], item)
    groups = []
    for url, observations in sorted(by_url.items()):
        if len(observations) < 2:
            continue
        members = [{"observation_id": item.get("id"), "source_id": sid,
                    "title": item["title"], "url": url}
                   for sid, item in sorted(observations.items())]
        groups.append({"canonical_url": url, "observations": members,
                       "document_identity": "same_canonical_url",
                       "independent_corroboration": False,
                       "same_event_label": None,
                       "review_status": "unreviewed"})
    return {"schema_version": 1,
            "purpose": "shared_document_provenance_not_positive_same_event_labels",
            "groups": groups[:limit],
            "coverage": {"shared_document_groups": len(groups), "selected_groups": min(len(groups), limit)}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("discovery", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()
    result = same_document_examples(json.loads(args.discovery.read_text(encoding="utf-8")), args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"]))


if __name__ == "__main__":
    main()
