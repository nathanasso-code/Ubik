#!/usr/bin/env python3
"""Public social author discovery pilot; metadata only, no publication or scoring.

Explicit queries and instances only. Bounded requests, per-source errors, no login.
"""
import argparse
import json
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser

class StripHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def plain(html):
    p = StripHTML()
    p.feed(html or "")
    return unescape(" ".join(" ".join(p.parts).split()))

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Ubik-source-discovery/0.1 (metadata research)", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.load(response)

def bluesky_candidates(query, limit=10):
    url = "https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors?" + urllib.parse.urlencode({"q": query, "limit": min(limit, 20)})
    data = fetch(url)
    return [{"platform": "bluesky", "handle": a.get("handle"), "display_name": a.get("displayName"), "description": a.get("description", ""), "profile_url": "https://bsky.app/profile/" + a["handle"], "identity_status": "unverified", "discovered_by": query} for a in data.get("actors", []) if a.get("handle")]

def mastodon_candidates(instance, query, limit=10):
    parsed = urllib.parse.urlsplit(instance)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port:
        raise ValueError("Mastodon instance must be a public HTTPS origin")
    origin = "https://" + parsed.hostname
    url = origin + "/api/v2/search?" + urllib.parse.urlencode({"q": query, "type": "accounts", "limit": min(limit, 20)})
    data = fetch(url)
    return [{"platform": "mastodon", "handle": a.get("acct"), "display_name": a.get("display_name"), "description": plain(a.get("note")), "profile_url": a.get("url"), "instance_searched": origin, "identity_status": "unverified", "discovered_by": query} for a in data.get("accounts", []) if a.get("url")]

def discover(queries, instances):
    results, errors = [], []
    for query in queries:
        try:
            results.extend(bluesky_candidates(query))
        except Exception as exc:
            errors.append({"platform": "bluesky", "query": query, "error": str(exc)[:240]})
        for instance in instances:
            try:
                results.extend(mastodon_candidates(instance, query))
            except Exception as exc:
                errors.append({"platform": "mastodon", "instance": instance, "query": query, "error": str(exc)[:240]})
    unique = {}
    for item in results:
        unique[(item["platform"], item["profile_url"])] = item
    return {"schema_version": 1, "status": "candidates_only", "candidates": list(unique.values()), "errors": errors, "disclaimer": "Public profile search is not evidence of expertise, identity verification, or endorsement."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--query", action="append", required=True)
    p.add_argument("--instance", action="append", default=[])
    p.add_argument("--output", required=True)
    a = p.parse_args()
    result = discover(a.query[:12], a.instance[:4])
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Public social candidates: {len(result['candidates'])}; errors: {len(result['errors'])}")
