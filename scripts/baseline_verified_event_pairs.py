#!/usr/bin/env python3
"""Make a transparent, conservative lexical baseline over a reviewed document set."""
import argparse
import json
import re
from pathlib import Path

STOP = {"with", "from", "that", "this", "more", "free", "users", "model",
        "models", "new", "openai", "announces", "launches", "unveils", "introducing"}


def tokens(title):
    return {x for x in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", title.lower())
            if len(x) >= 3 and x not in STOP}


def predict(reference, threshold=0.65):
    if not 0 <= threshold <= 1:
        raise ValueError("Invalid threshold")
    docs = {d["id"]: d for d in reference.get("documents", [])}
    pairs = []
    for item in reference.get("pairs", []):
        left, right = docs[item["left"]], docs[item["right"]]
        a, b = tokens(left["title"]), tokens(right["title"])
        similarity = len(a & b) / len(a | b) if a | b else 0
        # Only an unambiguous exact-title match is sufficient for this baseline.
        # All other cases abstain: title overlap cannot prove same-event identity.
        decision = ("same_event" if left["title"].strip().casefold() == right["title"].strip().casefold()
                    and left["url"] != right["url"] else "abstain")
        pairs.append({"left": item["left"], "right": item["right"],
                      "decision": decision, "title_jaccard": round(similarity, 6),
                      "method": "exact_title_distinct_url_or_abstain"})
    return {"method": "conservative_title_baseline", "threshold_informational_only": threshold,
            "pairs": pairs}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("reference", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    result = predict(json.loads(args.reference.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
