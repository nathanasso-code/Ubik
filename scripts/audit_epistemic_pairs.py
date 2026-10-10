#!/usr/bin/env python3
"""Audit candidate-pair concentration and risk, without assigning same-event labels."""
import argparse
import json
from collections import Counter
from pathlib import Path


def audit(payload, threshold=0.65):
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between zero and one")
    items = payload.get("items", [])
    source_pairs = Counter()
    above = []
    for row in items:
        left, right = row.get("left_source"), row.get("right_source")
        if left and right:
            source_pairs[tuple(sorted((left, right)))] += 1
        if row.get("similarity_hint", 0) >= threshold:
            above.append({
                "left_id": row.get("left_id"), "right_id": row.get("right_id"),
                "left_title": row.get("left_title"), "right_title": row.get("right_title"),
                "similarity_hint": row.get("similarity_hint"),
                "review_status": "unreviewed",
                "same_event_label": None
            })
    return {
        "schema_version": 1,
        "purpose": "candidate_diagnostics_not_event_classification",
        "threshold": threshold,
        "selected_pairs": len(items),
        "pairs_above_threshold": len(above),
        "same_url_pairs": sum(bool(row.get("same_url")) for row in items),
        "source_pair_distribution": [
            {"sources": list(pair), "count": count}
            for pair, count in sorted(source_pairs.items(), key=lambda x: (-x[1], x[0]))
        ],
        "review_priority": above,
        "warning": "High title similarity is not evidence of same event. These are not verified positives."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_file", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--threshold", type=float, default=0.65)
    args = parser.parse_args()
    result = audit(json.loads(args.candidate_file.read_text(encoding="utf-8")), args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected_pairs": result["selected_pairs"], "above_threshold": result["pairs_above_threshold"]}))


if __name__ == "__main__":
    main()
