#!/usr/bin/env python3
"""Audit reference-set coverage and guard against pair-level evaluation leakage.

A test split must hold out whole event/document components, not randomly selected
pairs that share articles with training data.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def audit(reference):
    documents = reference.get("documents", [])
    docs = {d["id"]: d for d in documents}
    if len(docs) != len(documents):
        raise ValueError("Duplicate document ID")
    seen_urls = {}
    for d in documents:
        if not d.get("url") or not d.get("title"):
            raise ValueError("Missing document title or URL")
        if d["url"] in seen_urls and seen_urls[d["url"]] != d["id"]:
            raise ValueError("Same URL used by distinct document IDs: document dedup first")
        seen_urls[d["url"]] = d["id"]
    parent = {key: key for key in docs}

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    counts = Counter()
    verified = []
    seen = set()
    for pair in reference.get("pairs", []):
        a, b = pair["left"], pair["right"]
        if a not in docs or b not in docs or a == b:
            raise ValueError("Invalid pair")
        key = tuple(sorted((a, b)))
        if key in seen:
            raise ValueError("Duplicate pair")
        seen.add(key)
        status = pair.get("review_status", "unreviewed")
        label = pair.get("label", "uncertain")
        if status == "verified" and label not in ("same_event", "different_event"):
            raise ValueError("Verified pairs require a binary event label")
        counts[status + ":" + label] += 1
        if status == "verified":
            verified.append((a, b, label))
            if label == "same_event":
                union(a, b)
    components = defaultdict(list)
    for doc in docs:
        components[root(doc)].append(doc)
    conflicts = [{"left": a, "right": b} for a, b, label in verified
                 if label == "different_event" and root(a) == root(b)]
    return {
        "documents": len(docs),
        "pairs": len(seen),
        "label_counts": dict(sorted(counts.items())),
        "verified_positive_pairs": counts["verified:same_event"],
        "verified_negative_pairs": counts["verified:different_event"],
        "event_components": [sorted(v) for v in sorted(components.values(), key=lambda v: min(v))],
        "distinct_positive_event_components": sum(len(v) > 1 for v in components.values()),
        "contradictions": conflicts,
        "held_out_evaluation_ready": not conflicts and
            counts["verified:same_event"] > 0 and counts["verified:different_event"] > 0 and
            sum(len(v) > 1 for v in components.values()) >= 2,
        "warning": "Readiness flag is only a minimal prerequisite; representative sampling and event-disjoint splitting remain necessary."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("reference", type=Path)
    args = p.parse_args()
    print(json.dumps(audit(json.loads(args.reference.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
