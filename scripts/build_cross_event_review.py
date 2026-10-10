#!/usr/bin/env python3
"""Prepare a human-review queue of cross-event negatives without claiming verification.

Distinct explicitly named event families may be useful hard-negative candidates,
but their identity must be reviewed against original content before scoring.
"""
import argparse
import json
from pathlib import Path


def negative_candidates(reference, limit=40):
    if type(limit) is not int or limit < 1:
        raise ValueError("Invalid limit")
    docs = reference.get("documents", [])
    candidates = []
    for i, left in enumerate(docs):
        for right in docs[i + 1:]:
            if left.get("event_family") and right.get("event_family") and left["event_family"] != right["event_family"]:
                candidates.append({
                    "left": left["id"], "right": right["id"],
                    "left_url": left["url"], "right_url": right["url"],
                    "left_event_family": left["event_family"],
                    "right_event_family": right["event_family"],
                    "proposed_label": "different_event",
                    "review_status": "unreviewed",
                    "verified": False,
                    "warning": "Event-family metadata is not a substitute for reviewing both articles."
                })
    return {"schema_version": 1, "candidates": candidates[:limit],
            "coverage": {"total": len(candidates), "selected": min(len(candidates), limit)}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("reference", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    result = negative_candidates(json.loads(args.reference.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"]))


if __name__ == "__main__":
    main()
