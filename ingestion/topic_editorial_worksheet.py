"""Bounded, evidence-grounded editorial worksheet, never an approval engine.

Provides a deterministic sample across source and evidence-gap strata.
"""
import argparse
import csv
import io
import json
from collections import defaultdict
from pathlib import Path

FIELDS = ["url", "title", "publisher", "source_ids", "area_ids",
          "content_type_candidate", "evidence_basis", "description_evidence",
          "review_reasons", "topic_relevance", "content_kind",
          "central_message", "central_message_evidence", "original_contribution",
          "importance_reason", "same_event_with_url", "independent_origin",
          "feed_decision", "reviewer_notes"]


def sample(review, *, limit=30):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be 1..100")
    items = review.get("items", [])
    buckets = defaultdict(list)
    for row in items:
        reasons = row.get("review_reasons", [])
        stratum = ("pair" if "possible_same_event_pair" in reasons else
                   "missing_evidence" if "missing_substantive_description" in reasons else
                   "no_area" if "no_specific_area" in reasons else "routine")
        buckets[(stratum, (row.get("source_ids") or ["unknown"])[0])].append(row)
    for rows in buckets.values():
        rows.sort(key=lambda x: x["url"])
    chosen, selected = [], set()
    # Cover all strata before filling; don't let a dominant source monopolize.
    for stratum in ("pair", "missing_evidence", "no_area", "routine"):
        sources = sorted(k for k in buckets if k[0] == stratum)
        while sources and len(chosen) < limit:
            remaining = []
            for key in sources:
                if len(chosen) >= limit:
                    break
                if buckets[key]:
                    row = buckets[key].pop(0)
                    if row["url"] not in selected:
                        chosen.append(row)
                        selected.add(row["url"])
                if buckets[key]:
                    remaining.append(key)
            sources = remaining
    return chosen


def worksheet(review, *, limit=30):
    rows = []
    for item in sample(review, limit=limit):
        rows.append({
            "url": item["url"], "title": item.get("title") or "",
            "publisher": item.get("publisher") or "",
            "source_ids": ", ".join(item.get("source_ids", [])),
            "area_ids": ", ".join(item.get("area_ids", [])),
            "content_type_candidate": item.get("content_type_candidate", "unclassified"),
            "evidence_basis": ("feed_description_verbatim"
                               if item.get("description_evidence") else "title_only"),
            "description_evidence": " | ".join(item.get("description_evidence", [])),
            "review_reasons": ", ".join(item.get("review_reasons", [])),
            "topic_relevance": "", "content_kind": "", "central_message": "",
            "central_message_evidence": "", "original_contribution": "",
            "importance_reason": "", "same_event_with_url": "",
            "independent_origin": "", "feed_decision": "", "reviewer_notes": "",
        })
    return rows


def render_csv(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("priority_review", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    review = json.loads(args.priority_review.read_text(encoding="utf-8"))
    rows = worksheet(review, limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_csv(rows), encoding="utf-8")
    print(json.dumps({"worksheet_rows": len(rows),
                      "unreviewed": len(rows), "publication_approvals": 0}))


if __name__ == "__main__":
    main()
