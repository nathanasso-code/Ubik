#!/usr/bin/env python3
"""Prepare article-review tasks for a bounded event family from the real RSS archive.

The queue is for finding cross-publisher event positives and hard negatives.
No automatically generated task receives a verified label.
"""
import argparse
import json
import re
from pathlib import Path

STOP = {"release", "launch", "announced", "announcement", "introducing", "model",
        "models", "new", "the", "and", "for", "with", "from", "openai",
        "google", "meta", "anthropic"}


def tokens(s):
    # Keep product-version identifiers; standalone numbers are not evidence.
    return {x for x in re.findall(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", s.lower())
            if len(x) >= 3 and x not in STOP and not x.isdigit()}


def distinctive_terms(s):
    return {x for x in tokens(s) if any(ch.isdigit() for ch in x)
            or "-" in x or "." in x}

def review_tasks(discovery, anchors, per_anchor=12):
    if type(per_anchor) is not int or per_anchor < 1:
        raise ValueError("per_anchor must be positive")
    items = discovery.get("items", [])
    tasks = []
    for anchor in anchors:
        terms = tokens(anchor["query"])
        distinctive = distinctive_terms(anchor["query"])
        scored = []
        for item in items:
            title = item.get("title", "")
            if not item.get("url") or not item.get("source_id") or not title:
                continue
            overlap = terms & tokens(title)
            if not overlap or (distinctive and not (overlap & distinctive)):
                continue
            if not distinctive and len(overlap) < min(2, len(terms)):
                continue
            scored.append((len(overlap), item))
        scored.sort(key=lambda x: (-x[0], x[1].get("source_id", ""), x[1]["url"]))
        selected, seen_sources = [], set()
        for score, item in scored:
            if item["source_id"] in seen_sources:
                continue
            selected.append({"observation_id": item.get("id"), "source_id": item["source_id"],
                             "title": item["title"], "url": item["url"],
                             "published_raw": item.get("published_raw"),
                             "query_overlap": score, "event_label": None,
                             "review_status": "unreviewed",
                             "evidence": None})
            seen_sources.add(item["source_id"])
            if len(selected) >= per_anchor:
                break
        tasks.append({"anchor_id": anchor["id"], "query": anchor["query"],
                      "candidate_observations": selected,
                      "status": "discovery_only"})
    return {"schema_version": 1, "purpose": "cross_source_event_review_tasks",
            "anchors": tasks, "verified_event_pairs": 0,
            "warning": "Title matches identify candidates only; they do not establish same-event identity."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("discovery", type=Path)
    p.add_argument("anchors", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    result = review_tasks(json.loads(args.discovery.read_text(encoding="utf-8")),
                          json.loads(args.anchors.read_text(encoding="utf-8"))["anchors"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"anchors": len(result["anchors"]),
                      "candidate_observations": sum(len(x["candidate_observations"]) for x in result["anchors"])}))


if __name__ == "__main__":
    main()
