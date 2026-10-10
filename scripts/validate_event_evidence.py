#!/usr/bin/env python3
"""Validate reviewed-event evidence before promoting pairs into an evaluation reference.

This is a structural gate, not a substitute for actually reading the linked articles.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


def validate(reference):
    docs = reference.get("documents", [])
    ids = set()
    issues = []
    for doc in docs:
        ident = doc.get("id")
        if not ident or ident in ids:
            issues.append({"kind": "invalid_document_id", "id": ident})
        ids.add(ident)
        url = doc.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            issues.append({"kind": "invalid_url", "id": ident})
        if not doc.get("title") or not doc.get("publisher"):
            issues.append({"kind": "missing_document_metadata", "id": ident})
    counts = Counter()
    seen = set()
    for pair in reference.get("pairs", []):
        a, b = pair.get("left"), pair.get("right")
        key = tuple(sorted((str(a), str(b))))
        if not a or not b or a == b or a not in ids or b not in ids or key in seen:
            issues.append({"kind": "invalid_or_duplicate_pair", "pair": [a, b]})
        seen.add(key)
        label = pair.get("label")
        status = pair.get("review_status", "unreviewed")
        counts[f"{status}:{label}"] += 1
        if status == "verified":
            if label not in ("same_event", "different_event"):
                issues.append({"kind": "verified_label_invalid", "pair": [a, b]})
            if not pair.get("basis"):
                issues.append({"kind": "missing_pair_basis", "pair": [a, b]})
            for ident in (a, b):
                doc = next((d for d in docs if d.get("id") == ident), {})
                if not doc.get("evidence") or not doc.get("date"):
                    issues.append({"kind": "missing_document_evidence", "id": ident})
    return {"valid_structure": not issues, "issues": issues, "counts": dict(counts),
            "warning": "Passing structural checks does not establish factual verification or independent corroboration."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("reference", type=Path)
    args = p.parse_args()
    report = validate(json.loads(args.reference.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    if not report["valid_structure"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
