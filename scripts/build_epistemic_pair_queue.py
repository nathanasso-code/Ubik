#!/usr/bin/env python3
"""Produce unverified review pairs from a discovery review queue; never infer event identity."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

STOP = set("the and for with from into that this are was were how what why about over under new more not but its has have can using via part update paper study research model models ai artificial intelligence".split())


def tokens(text):
    return set(t for t in re.findall(r"[\w]+", (text or "").casefold()) if len(t) >= 3 and t not in STOP and not t.isdigit())


def candidate_pairs(queue, limit=40):
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("Positive limit required")
    items = queue.get("items", [])
    by_id = {x["observation_id"]: x for x in items}
    if len(by_id) != len(items):
        raise ValueError("Duplicate observation identifiers")
    tokenized = {i: tokens(x.get("title", "")) for i, x in by_id.items()}
    counts = Counter(t for ts in tokenized.values() for t in ts)
    n = max(len(items), 1)
    weighted = {}
    for i, ts in tokenized.items():
        weighted[i] = {t: math.log(1 + n / (1 + counts[t])) for t in ts}
    ranked = []
    ids = sorted(by_id)
    for index, a in enumerate(ids):
        for b in ids[index + 1:]:
            left, right = by_id[a], by_id[b]
            if left.get("url") == right.get("url"):
                relation = "same_url"
                similarity = 1.0
            else:
                common = tokenized[a] & tokenized[b]
                numerator = sum(min(weighted[a][t], weighted[b][t]) for t in common)
                denominator = sum(weighted[a].values()) + sum(weighted[b].values()) - numerator
                similarity = numerator / denominator if denominator else 0
                relation = "title_token_overlap"
            if similarity > 0:
                ranked.append((similarity, a, b, relation))
    ranked.sort(key=lambda x: (-x[0], x[1], x[2]))
    return {
        "schema_version": 1,
        "purpose": "unverified_pairs_for_manual_same_event_review",
        "method": "weighted_title_token_overlap_not_event_classifier",
        "items": [{
            "left_id": a, "right_id": b,
            "left_title": by_id[a].get("title"), "right_title": by_id[b].get("title"),
            "left_url": by_id[a].get("url"), "right_url": by_id[b].get("url"),
            "left_source": by_id[a].get("source_id"), "right_source": by_id[b].get("source_id"),
            "similarity_hint": round(score, 5), "reason": reason,
            "same_event_label": None, "review_status": "unreviewed",
        } for score, a, b, reason in ranked[:limit]],
        "coverage": {"input_observations": len(items), "nonzero_candidate_pairs": len(ranked), "selected_pairs": min(limit, len(ranked))}
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    data = candidate_pairs(json.loads(args.queue.read_text(encoding="utf-8")), args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["coverage"]))


if __name__ == "__main__":
    main()
