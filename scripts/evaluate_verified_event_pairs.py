#!/usr/bin/env python3
"""Evaluate pair decisions only against explicitly reviewed event labels.

No gold label is inferred from title similarity or publisher counts.
"""
import argparse
import json
from pathlib import Path


def evaluate(reference, predictions):
    docs = {d["id"]: d for d in reference.get("documents", [])}
    labels = {}
    for pair in reference.get("pairs", []):
        a, b = pair["left"], pair["right"]
        if a == b or a not in docs or b not in docs:
            raise ValueError("Invalid reference document")
        if pair.get("review_status") != "verified" or pair.get("label") not in ("same_event", "different_event"):
            continue
        key = tuple(sorted((a, b)))
        if key in labels:
            raise ValueError("Duplicate reference pair")
        labels[key] = pair["label"] == "same_event"
    decisions = {}
    for pair in predictions.get("pairs", []):
        key = tuple(sorted((pair["left"], pair["right"])))
        if key in decisions:
            raise ValueError("Duplicate prediction")
        decision = pair.get("decision")
        if decision not in ("same_event", "different_event", "abstain"):
            raise ValueError("Invalid prediction")
        decisions[key] = decision
    tp = fp = fn = tn = abstain = 0
    for key, expected in labels.items():
        actual = decisions.get(key, "abstain")
        if actual == "abstain":
            abstain += 1
        elif actual == "same_event":
            tp += int(expected)
            fp += int(not expected)
        else:
            fn += int(expected)
            tn += int(not expected)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn + sum(labels[k] for k in labels if decisions.get(k, "abstain") == "abstain")) if any(labels.values()) else None
    return {"verified_reference_pairs": len(labels), "tp": tp, "fp": fp,
            "fn": fn, "tn": tn, "abstained": abstain,
            "precision_on_merges": precision,
            "recall_including_abstentions_as_missed": recall,
            "warning": "Pair-level metrics only; small or nonrepresentative reference sets cannot establish production accuracy."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("reference", type=Path)
    p.add_argument("predictions", type=Path)
    args = p.parse_args()
    print(json.dumps(evaluate(json.loads(args.reference.read_text(encoding="utf-8")),
                              json.loads(args.predictions.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
