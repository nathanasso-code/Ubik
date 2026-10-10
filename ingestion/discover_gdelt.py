#!/usr/bin/env python3
"""Explicit opt-in GDELT DOC discovery. No network calls without --live."""
import argparse
import json
from pathlib import Path
from ingestion.gdelt_doc import collect, request_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Explicit search scope; not a complete news feed")
    parser.add_argument("--timespan", default="1h")
    parser.add_argument("--maxrecords", type=int, default=75)
    parser.add_argument("--output", type=Path, default=Path("data/discovery/gdelt-doc.json"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    request_url(args.query, timespan=args.timespan, maxrecords=args.maxrecords)
    if not args.live:
        print("Dry run: --live required to contact GDELT DOC")
        return
    result = collect(args.query, timespan=args.timespan, maxrecords=args.maxrecords)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"observations": len(result["observations"]),
                      "potentially_truncated": result["potentially_truncated"]}))


if __name__ == "__main__":
    main()
