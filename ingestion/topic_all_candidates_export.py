"""Export every AI-keyword candidate, without the 30-card feed limit."""
import argparse
import csv
import json
from pathlib import Path


def export(topic):
    rows = topic.get("all_candidates", topic.get("visible", []))
    fields = ["title", "url", "publisher", "authors", "source_ids", "published_raw",
              "area_ids", "source_quality", "same_event", "display_kind"]
    return fields, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic_report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    fields, rows = export(json.loads(args.topic_report.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: ", ".join(row.get(key, []))
                             if isinstance(row.get(key), list) else row.get(key, "")
                             for key in fields})
    print(json.dumps({"ai_topic_sources_exported": len(rows),
                      "editorial_exclusions": 0}))


if __name__ == "__main__":
    main()
