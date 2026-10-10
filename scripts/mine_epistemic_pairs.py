#!/usr/bin/env python3
"""Mine title-overlap candidate pairs across the full discovery archive.

Unverified suggestions only; no clustering, no truth or independence claims.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

STOP = set("the and for with from into that this are was were how what why about over under new more not but its has have can using via part update paper study research model models ai artificial intelligence".split())


def tokens(title):
    return {x for x in re.findall(r"[\w]+", (title or "").casefold()) if len(x) >= 4 and x not in STOP and not x.isdigit()}


def mine(discovery, limit=60, min_shared=2):
    if limit < 1 or min_shared < 1:
        raise ValueError("Positive limits required")
    items = [x for x in discovery.get("items", []) if x.get("url") and x.get("title") and x.get("source_id")]
    # Stable deduplication of repeated observations within a feed.
    unique = {}
    for x in sorted(items, key=lambda v: (v["source_id"], v["url"], v.get("id", ""))):
        unique.setdefault((x["source_id"], x["url"]), x)
    rows = list(unique.values())
    inverted = defaultdict(list)
    for index, row in enumerate(rows):
        for token in tokens(row["title"]):
            inverted[token].append(index)
    overlap = defaultdict(int)
    for postings in inverted.values():
        # Suppress very frequent terms; avoid quadratic explosion from generic vocabulary.
        if len(postings) > max(40, len(rows) // 15):
            continue
        for i, a in enumerate(postings):
            for b in postings[i + 1:]:
                if rows[a]["source_id"] != rows[b]["source_id"]:
                    overlap[(a, b)] += 1
    ranked = []
    for (a, b), shared in overlap.items():
        if shared < min_shared:
            continue
        left, right = rows[a], rows[b]
        ta, tb = tokens(left["title"]), tokens(right["title"])
        union = len(ta | tb)
        score = len(ta & tb) / union if union else 0
        ranked.append((score, shared, a, b))
    ranked.sort(key=lambda x: (-x[0], -x[1], rows[x[2]]["url"], rows[x[3]]["url"]))
    selected = []
    for score, shared, a, b in ranked[:limit]:
        left, right = rows[a], rows[b]
        selected.append({
            "left_id": left.get("id"), "right_id": right.get("id"),
            "left_title": left["title"], "right_title": right["title"],
            "left_url": left["url"], "right_url": right["url"],
            "left_source": left["source_id"], "right_source": right["source_id"],
            "same_url": left["url"] == right["url"],
            "shared_title_tokens": shared, "similarity_hint": round(score, 5),
            "same_event_label": None, "review_status": "unreviewed"
        })
    return {"schema_version": 1, "purpose": "cross_source_unverified_event_review_candidates",
            "method": "inverted_title_token_index_jaccard",
            "items": selected,
            "coverage": {"input_observations": len(items), "unique_source_url_observations": len(rows),
                         "cross_source_candidate_pairs": len(ranked), "selected_pairs": len(selected)}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("discovery", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--limit", type=int, default=60)
    args = p.parse_args()
    result = mine(json.loads(args.discovery.read_text(encoding="utf-8")), args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"]))


if __name__ == "__main__":
    main()
