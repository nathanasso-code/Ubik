#!/usr/bin/env python3
"""Create an auditable human-readable coverage report from a completed discovery artifact."""
import argparse
import json
from pathlib import Path

def report(data):
    stats = data.get("coverage", {})
    lines = ["# Ubik — AI sources acquisition report", "", f"Retrieved at: {data.get('retrieved_at', 'unknown')}", "", "## Coverage"]
    for key in ("enabled_feeds", "successful_feeds", "failed_feeds", "stored_items", "items_with_named_author", "items_missing_named_author", "items_with_publication_date"):
        lines.append(f"- {key}: {stats.get(key, 'not recorded')}")
    lines += ["", "## Source health", "", "| Feed | Result | Items seen | New | With author | Missing author |", "|---|---|---:|---:|---:|---:|"]
    for item in data.get("source_reports", []):
        vals = [item.get("source_id", "?"), item.get("status", "?"), str(item.get("seen", 0)), str(item.get("new", 0)), str(item.get("with_named_author", 0)), str(item.get("missing_named_author", 0))]
        lines.append("| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in vals) + " |")
    lines += ["", "## Interpretation", "", "A successful fetch confirms technical availability at retrieval time, not completeness, independence, reliability or factual validation.", "An absent byline is not automatically an error: some publications are institutional or feeds omit author metadata.", "Failures require inspection before treating a source as inaccessible.", ""]
    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report(data), encoding="utf-8")
    print(f"Wrote {args.output}")
