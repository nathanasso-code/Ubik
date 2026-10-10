#!/usr/bin/env python3
"""Low-cost, metadata-only Hacker News ingestion pilot.

Uses the documented public Firebase API. No article scraping, no ranking,
no automatic claims of corroboration. Dry-run by default.
"""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://hacker-news.firebaseio.com/v0/"
USER_AGENT = "Ubik research pilot (metadata only; contact via repository)"


def fetch_json(path, timeout=12):
    if not path.startswith(("newstories.json", "item/")) or ".." in path:
        raise ValueError("Unsupported API path")
    req = Request(BASE + path, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def normalize_story(story):
    if not isinstance(story, dict) or story.get("type") != "story" or story.get("dead") or story.get("deleted"):
        return None
    ident = story.get("id")
    if not isinstance(ident, int) or not isinstance(story.get("title"), str) or not story["title"].strip():
        return None
    discussion_url = f"https://news.ycombinator.com/item?id={ident}"
    target_url = story.get("url") or discussion_url
    if not isinstance(target_url, str) or not target_url.startswith(("https://", "http://")):
        target_url = discussion_url
    published = story.get("time")
    published_iso = (datetime.fromtimestamp(published, tz=timezone.utc).isoformat()
                     if isinstance(published, int) and published >= 0 else None)
    return {
        "id": "hn-" + str(ident),
        "source_id": "hacker-news-newstories",
        "kind": "social_link",
        "title": story["title"].strip(),
        "url": target_url,
        "original_url": discussion_url,
        "published_raw": published_iso,
        "provenance": "public_hacker_news_api_metadata",
        "validation": "not_assessed",
        "score_at_observation": story.get("score"),
        "comments_at_observation": story.get("descendants"),
        "author": story.get("by"),
        "external_document_id": hashlib.sha256(target_url.encode()).hexdigest()[:20],
    }


def collect(limit, pause_seconds=0.15, fetch=fetch_json, sleep=time.sleep):
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    ids = fetch("newstories.json")
    if not isinstance(ids, list):
        raise ValueError("Unexpected story list")
    observations = []
    errors = []
    for ident in ids[:limit]:
        if not isinstance(ident, int):
            continue
        try:
            record = normalize_story(fetch(f"item/{ident}.json"))
            if record:
                observations.append(record)
        except (OSError, ValueError, TimeoutError) as exc:
            errors.append({"id": ident, "error_type": type(exc).__name__})
        sleep(pause_seconds)
    return {"schema_version": 1, "connector": "hacker_news_newstories",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "requested": limit, "observations": observations, "errors": errors,
            "note": "Observations are discovery signals, not independent publisher confirmations."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--output", type=Path, default=Path("data/discovery/hacker-news.json"))
    parser.add_argument("--live", action="store_true", help="Explicitly allow public API calls")
    args = parser.parse_args()
    if not args.live:
        print("Dry run: pass --live to fetch the public Hacker News API")
        return
    result = collect(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"observations": len(result["observations"]), "errors": len(result["errors"])}))


if __name__ == "__main__":
    main()
