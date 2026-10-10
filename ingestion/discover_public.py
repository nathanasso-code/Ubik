"""Opt-in CLI for independent social and scientific metadata acquisition."""
import argparse
import json
from pathlib import Path

from .public_adapters import (bluesky_collect, bluesky_url, mastodon_collect,
                              mastodon_url, openalex_collect, openalex_url)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="provider", required=True)
    b = sub.add_parser("bluesky")
    b.add_argument("--actor", required=True)
    b.add_argument("--limit", type=int, default=30)
    b.add_argument("--cursor")
    m = sub.add_parser("mastodon")
    m.add_argument("--instance", required=True)
    m.add_argument("--limit", type=int, default=20)
    m.add_argument("--max-id")
    o = sub.add_parser("openalex")
    o.add_argument("--from-date", required=True)
    o.add_argument("--to-date", required=True)
    o.add_argument("--per-page", type=int, default=50)
    o.add_argument("--cursor", default="*")
    p.add_argument("--live", action="store_true")
    p.add_argument("--output", type=Path, default=Path("data/discovery/public-adapter.json"))
    args = p.parse_args()
    if args.provider == "bluesky":
        url = bluesky_url(args.actor, args.limit, args.cursor)
        run = lambda: bluesky_collect(args.actor, args.limit, args.cursor)
    elif args.provider == "mastodon":
        url = mastodon_url(args.instance, args.limit, args.max_id)
        run = lambda: mastodon_collect(args.instance, args.limit, args.max_id)
    else:
        url = openalex_url(args.from_date, args.to_date, args.per_page, args.cursor)
        run = lambda: openalex_collect(args.from_date, args.to_date, args.per_page, args.cursor)
    if not args.live:
        print("Dry run; --live required. Endpoint:", url)
        return
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"connector": result["connector"], "observations": len(result["observations"]),
                      "invalid": result["invalid"]}))


if __name__ == "__main__":
    main()
