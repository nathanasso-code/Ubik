"""Generate a review-only issue seed report from an existing topic evidence JSON."""
import argparse
import json
from pathlib import Path
from .issue_candidates import propose_issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_json", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    report = json.loads(args.evidence_json.read_text(encoding="utf-8"))
    output = propose_issues(report, limit=args.limit)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"topic_id": output["topic_id"], "candidate_count": output["candidate_count"],
                      "visible_count": output["visible_count"], "published": 0}))


if __name__ == "__main__":
    main()
