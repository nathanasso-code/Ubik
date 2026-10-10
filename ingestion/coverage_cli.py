"""Generate a reproducible source inventory and acquisition-quality report offline.

Optional historical discovery and federated files are read, never fetched.
"""
import argparse
import json
from pathlib import Path

from .coverage_report import evaluate_coverage
from .cross_topic_inventory import cross_topic_inventory
from .channel_readiness import assess_channels
from .feed_triage import triage_feed_reports
from .source_inventory import inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--discovery", type=Path, help="Historical RSS discovery JSON")
    parser.add_argument("--federated", type=Path, help="Unselected federated observation JSON")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalog = inventory(args.root)
    discovery = json.loads(args.discovery.read_text(encoding="utf-8")) if args.discovery else None
    federated = json.loads(args.federated.read_text(encoding="utf-8")) if args.federated else None
    cross_topic = cross_topic_inventory(args.root)
    result = {"cross_topic_inventory": cross_topic,
              "channel_readiness": assess_channels(cross_topic),
              "feed_triage": triage_feed_reports((discovery or {}).get("source_reports", [])),
              "inventory": catalog,
              "coverage": evaluate_coverage(catalog, discovery=discovery, federated=federated),
              "input_files": {"discovery": str(args.discovery) if args.discovery else None,
                              "federated": str(args.federated) if args.federated else None}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"cross_topic_entries": result["cross_topic_inventory"]["total_entries"],
                      "registry_entries": catalog["registry_entries"],
                      "enabled_rss": catalog["enabled_rss"],
                      "tested_feeds": result["coverage"]["tested_feed_count"],
                      "observations": result["coverage"]["observations_audited"],
                      "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
