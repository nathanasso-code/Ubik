"""Validate completed editorial annotations and summarize agreement-ready counts.

No automatic publication, no truth claims, no inferred labels.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ALLOWED = {
    "topic_relevance": {"yes", "no", "uncertain"},
    "content_kind": {"event", "research", "opinion", "product", "other"},
    "original_contribution": {"yes", "no", "uncertain"},
    "independent_origin": {"yes", "no", "unknown"},
    "feed_decision": {"include", "exclude", "defer"},
}
REQUIRED = {"url", "title", "topic_relevance", "content_kind",
            "central_message", "central_message_evidence",
            "original_contribution", "importance_reason",
            "same_event_with_url", "independent_origin", "feed_decision"}
DECISION_FIELDS = list(ALLOWED) + ["central_message", "central_message_evidence",
                                   "importance_reason"]


def validate(rows, known_urls=None):
    errors, accepted, pending, seen = [], [], [], set()
    known_urls = set(known_urls) if known_urls is not None else None
    for index, row in enumerate(rows, 2):
        url = (row.get("url") or "").strip()
        if not url or url in seen:
            errors.append({"row": index, "field": "url", "issue": "missing_or_duplicate"})
        seen.add(url)
        if known_urls is not None and url not in known_urls:
            errors.append({"row": index, "field": "url", "issue": "not_in_sample"})
        supplied = any((row.get(field) or "").strip() for field in DECISION_FIELDS)
        if not supplied:
            pending.append(url)
            continue
        for field in REQUIRED:
            if field not in row:
                errors.append({"row": index, "field": field, "issue": "missing_column"})
        for field, allowed in ALLOWED.items():
            value = (row.get(field) or "").strip().lower()
            if value not in allowed:
                errors.append({"row": index, "field": field, "issue": "invalid_or_missing_value"})
        for field in ("central_message", "central_message_evidence", "importance_reason"):
            if not (row.get(field) or "").strip():
                errors.append({"row": index, "field": field, "issue": "required_for_review"})
        relation = (row.get("same_event_with_url") or "").strip()
        if relation and (relation == url or (known_urls is not None and relation not in known_urls)):
            errors.append({"row": index, "field": "same_event_with_url",
                           "issue": "self_reference_or_outside_sample"})
        if (row.get("topic_relevance") or "").strip().lower() == "no" and (row.get("feed_decision") or "").strip().lower() == "include":
            errors.append({"row": index, "field": "feed_decision",
                           "issue": "cannot_include_off_topic"})
        accepted.append(row)
    return {
        "schema_version": 1, "rows": len(rows), "completed_rows": len(accepted),
        "pending_rows": len(pending), "errors": errors, "valid": not errors,
        "decisions": dict(Counter((r.get("feed_decision") or "").strip().lower()
                                  for r in accepted)),
        "caveat": "Validation checks completeness and internal consistency, not factual accuracy or editorial quality.",
        "publication_approvals": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("worksheet", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    with args.worksheet.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    report = validate(rows, known_urls=[r["url"] for r in rows])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"rows": report["rows"], "completed": report["completed_rows"],
                      "pending": report["pending_rows"], "errors": len(report["errors"])}))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
