"""Generate auditable SAME-EVENT review suggestions from selected topic sources.

Similarity only nominates a pair; never auto-merges, publishes or validates.
"""
import argparse
import itertools
import json
import re
from pathlib import Path

STOP = {"about", "after", "their", "these", "those", "with", "from",
        "that", "this", "into", "model", "models", "language",
        "artificial", "intelligence", "research", "new", "using",
        "paper", "study", "says", "latest", "released", "release"}


def tokens(title):
    return {word for word in re.findall(r"[a-z0-9]+", (title or "").casefold())
            if len(word) >= 4 and word not in STOP}


def suggest(report, *, limit=40, min_shared=3):
    if not 1 <= limit <= 200:
        raise ValueError("limit must be 1..200")
    rows = report.get("visible", [])
    pairs = []
    for left, right in itertools.combinations(rows, 2):
        if left["url"] == right["url"]:
            continue
        if set(left.get("source_ids", [])) & set(right.get("source_ids", [])):
            continue
        a, b = tokens(left.get("title")), tokens(right.get("title"))
        shared = a & b
        if len(shared) < min_shared:
            continue
        overlap = len(shared) / max(1, min(len(a), len(b)))
        pairs.append({
            "left": {"url": left["url"], "title": left.get("title"),
                     "publisher": left.get("publisher")},
            "right": {"url": right["url"], "title": right.get("title"),
                      "publisher": right.get("publisher")},
            "shared_title_terms": sorted(shared),
            "overlap_candidate_score": round(overlap, 3),
            "review_status": "unverified_same_event_candidate",
            "required_checks": [
                "Confirm identical bounded event, actor, date and scope",
                "Inspect both original documents; titles are insufficient",
                "Check syndication, citations and shared upstream origin",
            ],
        })
    pairs.sort(key=lambda p: (-p["overlap_candidate_score"],
                              p["left"]["url"], p["right"]["url"]))
    return {
        "schema_version": 1,
        "topic_id": report.get("topic", {}).get("id"),
        "sample_size": len(rows),
        "candidate_pairs": len(pairs),
        "review_pairs": pairs[:limit],
        "automatic_merges": 0,
        "note": "Title-only overlap is a review queue, NOT same-event evidence. "
                "Zero suggested pairs does not mean zero shared events.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic_report", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    result = suggest(json.loads(args.topic_report.read_text(encoding="utf-8")),
                     limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"topic_candidate_pairs": result["candidate_pairs"],
                      "review_pairs": len(result["review_pairs"]),
                      "automatic_merges": 0}))


if __name__ == "__main__":
    main()
