"""Prioritize human review using explicit evidence gaps, not a newsworthiness score.

This queue never changes acquisition, publication or event clustering.
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def build(topic_report, evidence_report, pairs_report):
    by_url = {row["url"]: row for row in evidence_report.get("items", [])}
    pairs = pairs_report.get("review_pairs", [])
    linked = {}
    for pair in pairs:
        for side in ("left", "right"):
            url = pair[side]["url"]
            linked[url] = linked.get(url, 0) + 1
    queue = []
    for row in topic_report.get("all_candidates", topic_report.get("visible", [])):
        url = row["url"]
        evidence = by_url.get(url, {})
        reasons = []
        if not evidence.get("description_evidence"):
            reasons.append("missing_substantive_description")
        if not row.get("area_ids"):
            reasons.append("no_specific_area")
        if linked.get(url):
            reasons.append("possible_same_event_pair")
        if not row.get("published_raw"):
            reasons.append("missing_publication_date")
        if not reasons:
            reasons.append("routine_content_review")
        queue.append({
            "url": url,
            "title": row.get("title"),
            "publisher": row.get("publisher"),
            "source_ids": row.get("source_ids", []),
            "area_ids": row.get("area_ids", []),
            "published_raw": row.get("published_raw"),
            "description_evidence": evidence.get("description_evidence", []),
            "content_type_candidate": evidence.get("content_type_candidate", "unclassified"),
            "review_reasons": reasons,
            "same_event_pair_count": linked.get(url, 0),
            "review_decision": "unreviewed",
            "claim_verified": False,
        })
    # Review order is about *uncertainty*, not importance or publication priority.
    priority = {"possible_same_event_pair": 0, "missing_substantive_description": 1,
                "no_specific_area": 2, "missing_publication_date": 3,
                "routine_content_review": 4}
    queue.sort(key=lambda x: (min(priority[r] for r in x["review_reasons"]),
                              x["url"]))
    return {
        "schema_version": 1,
        "topic_id": topic_report.get("topic", {}).get("id"),
        "documents_for_review": len(queue),
        "reason_counts": dict(Counter(reason for item in queue
                                      for reason in item["review_reasons"])),
        "items": queue,
        "publication_approved": 0,
        "automatic_event_merges": 0,
        "meaning": "Review urgency and evidence gaps only; NOT editorial importance.",
        "required_reviewer_fields": [
            "topic_relevance: yes/no/uncertain",
            "content_kind: event/research/opinion/product/other",
            "source_message: attributed text plus evidence span",
            "importance: reasoned human assessment",
            "event_identity: exact event or standalone",
            "independent_origin: yes/no/unknown",
            "feed_decision: include/exclude/defer",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic_report", type=Path)
    parser.add_argument("evidence_report", type=Path)
    parser.add_argument("pairs_report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = build(*(json.loads(p.read_text(encoding="utf-8")) for p in
                   (args.topic_report, args.evidence_report, args.pairs_report)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"review_documents": data["documents_for_review"],
                      "review_reasons": data["reason_counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
