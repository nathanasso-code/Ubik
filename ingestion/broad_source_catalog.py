"""Broad source-first discovery catalogue. No editorial exclusion for uncertainty.

All valid acquired URLs are retained, including undated and non-AI documents.
"""
import argparse
import csv
import io
import json
from collections import defaultdict
from pathlib import Path
from ingestion.topic_feed_pilot import classify, _date


def build(discovery):
    grouped = defaultdict(list)
    rejected = []
    for item in discovery.get("items", []):
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        if not url.startswith(("https://", "http://")) or not title:
            rejected.append({"url": url, "reason": "missing_title_or_valid_url"})
            continue
        grouped[url].append(item)
    rows = []
    for url, observations in grouped.items():
        primary = max(observations, key=lambda x: (len(x.get("description") or ""),
                                                    bool(x.get("published_raw"))))
        areas, explicit = classify(primary)
        # Relevance is a routing hint, not a quality or inclusion verdict.
        relevance = "explicit_ai_signal" if explicit else "needs_topic_review"
        rows.append({
            "url": url, "title": primary["title"],
            "publisher": primary.get("publisher") or "",
            "authors": primary.get("authors", []),
            "source_ids": sorted({x.get("source_id", "") for x in observations}),
            "published_raw": primary.get("published_raw"),
            "description": primary.get("description") or "",
            "area_ids": areas, "relevance_hint": relevance,
            "review_status": "unreviewed",
            "editorial_exclusion": False,
            "same_url_observations": len(observations),
            "source_independence": "unassessed",
        })
    rows.sort(key=lambda r: (-(_date(r["published_raw"]).timestamp()
                              if _date(r["published_raw"]) else -1e20), r["url"]))
    return {
        "schema_version": 1, "scope": "all_acquired_sources_no_recency_cutoff",
        "documents": len(rows), "invalid_records": len(rejected),
        "explicit_ai_signal": sum(x["relevance_hint"] == "explicit_ai_signal" for x in rows),
        "needs_topic_review": sum(x["relevance_hint"] == "needs_topic_review" for x in rows),
        "editorially_excluded": 0,
        "excluded_records": rejected,
        "items": rows,
        "policy": "Only invalid records are rejected; same-URL observations are consolidated with provenance. Uncertain, older and off-topic candidates remain accessible for human evaluation.",
    }


def to_csv(result):
    out = io.StringIO()
    fields = ["title", "url", "publisher", "authors", "source_ids",
              "published_raw", "relevance_hint", "area_ids", "description",
              "review_status", "editorial_exclusion", "same_url_observations"]
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for item in result["items"]:
        writer.writerow({key: ", ".join(item[key]) if isinstance(item.get(key), list)
                         else item.get(key, "") for key in fields})
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("discovery", type=Path)
    parser.add_argument("json_output", type=Path)
    parser.add_argument("csv_output", type=Path)
    args = parser.parse_args()
    result = build(json.loads(args.discovery.read_text(encoding="utf-8")))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.csv_output.write_text(to_csv(result), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("documents", "invalid_records", "explicit_ai_signal", "needs_topic_review", "editorially_excluded")}))


if __name__ == "__main__":
    main()
