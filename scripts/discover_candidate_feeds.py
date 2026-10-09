#!/usr/bin/env python3
"""Bounded RSS/Atom auto-discovery for curated candidate sites.

Produces a review queue; never changes enabled source registry.
"""
import argparse
import html.parser
import json
import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request

class FeedLinks(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        a = dict(attrs)
        if "alternate" in a.get("rel", "").lower().split() and a.get("type", "").lower() in ("application/rss+xml", "application/atom+xml", "application/feed+json") and a.get("href"):
            self.links.append(a["href"])

def validate_public_https(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Candidate must use public HTTPS")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("Candidate hostname cannot be resolved") from exc
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError("Candidate resolves to non-public address")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Redirect requires separate review")


def discover(url):
    validate_public_https(url)
    req = urllib.request.Request(url, headers={"User-Agent": "Ubik-feed-discovery/0.1"})
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(req, timeout=12) as response:
        final_url = response.geturl()
        if urllib.parse.urlsplit(final_url).scheme != "https":
            raise ValueError("Insecure redirect")
        body = response.read(512000).decode("utf-8", errors="replace")
    parser = FeedLinks()
    parser.feed(body)
    feeds = []
    for href in parser.links:
        target = urllib.parse.urljoin(final_url, href)
        p = urllib.parse.urlsplit(target)
        if p.scheme == "https" and p.hostname and not p.username and not p.password and target not in feeds:
            feeds.append(target)
    return feeds

def run(registry):
    results = []
    for candidate in registry.get("candidates", []):
        entry = {"id": candidate["id"], "name": candidate["name"], "page_url": candidate["url"], "status": "unverified", "feed_urls": []}
        try:
            entry["feed_urls"] = discover(candidate["url"])
            entry["status"] = "found" if entry["feed_urls"] else "not_advertised"
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)[:200]
        results.append(entry)
    return {"schema_version": 1, "promotion_requires_review": True, "results": results}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("registry")
    p.add_argument("output")
    a = p.parse_args()
    with open(a.registry, encoding="utf-8") as f:
        registry = json.load(f)
    result = run(registry)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Candidate sites checked: {len(result['results'])}; feeds advertised: {sum(x['status'] == 'found' for x in result['results'])}")
