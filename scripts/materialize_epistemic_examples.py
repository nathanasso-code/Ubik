#!/usr/bin/env python3
"""Join provisional pair labels to their immutable source evidence; never auto-promote to gold."""
import argparse
import json
from collections import Counter
from pathlib import Path

LABELS = {"same_event", "different_event", "uncertain"}


def materialize(seed, candidates):
    rows = candidates.get("items", [])
    output = []
    seen = set()
    for entry in seed.get("entries", []):
        index = entry.get("candidate_index")
        if type(index) is not int or index < 0 or index >= len(rows) or index in seen:
            raise ValueError("Invalid or duplicate candidate index")
        seen.add(index)
        label = entry.get("label")
        if label not in LABELS:
            raise ValueError("Unsupported label")
        source = rows[index]
        for key in ("left_url", "right_url", "left_title", "right_title", "left_source", "right_source"):
            if not source.get(key):
                raise ValueError("Missing provenance: " + key)
        output.append({
            "candidate_index": index,
            "left": {k: source["left_" + k] for k in ("url", "title", "source")},
            "right": {k: source["right_" + k] for k in ("url", "title", "source")},
            "similarity_hint": source.get("similarity_hint"),
            "label": label,
            "rationale": entry.get("rationale", ""),
            "review_basis": entry.get("review_basis"),
            "full_text_verified": entry.get("full_text_verified") is True,
            "review_status": entry.get("review_status", "provisional"),
        })
    counts = Counter(x["label"] for x in output)
    return {
        "schema_version": 1, "dataset": seed.get("dataset"),
        "origin": seed.get("origin"),
        "purpose": "review_dataset_not_gold_standard",
        "entries": output,
        "summary": {"total": len(output), "same_event": counts["same_event"],
                    "different_event": counts["different_event"], "uncertain": counts["uncertain"],
                    "gold_standard_eligible": sum(x["review_status"] == "verified" and x["full_text_verified"] for x in output)}
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("seed", type=Path)
    p.add_argument("candidates", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    result = materialize(json.loads(args.seed.read_text(encoding="utf-8")),
                         json.loads(args.candidates.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"]))


if __name__ == "__main__":
    main()
