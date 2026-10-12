"""Source-first catalogue from social discoveries, compatible with Ubik's URL catalogue.

No network fetch, ranking, editorial validation or production writes.
"""
import re
from collections import defaultdict
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit
from .contracts import canonical_url_hint


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(unescape(href))


def external_links(post):
    parser = _Links()
    parser.feed(post.get("content_html") or "")
    urls = parser.links + [u for u in re.findall(r'https?://[^\\s<>"]+', unescape(post.get("content_html") or ""))]
    for card in (post.get("card"),):
        if isinstance(card, dict) and card.get("url"):
            urls.append(card["url"])
    found = []
    social_hosts = {"mastodon.social", "bsky.app", "mastodon.online"}
    for url in urls:
        try:
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.lower() in social_hosts:
                continue
            key = canonical_url_hint(url)
            if key not in found:
                found.append(key)
        except (ValueError, TypeError):
            continue
    return found


def build_source_candidates(posts, existing=None):
    """Discover original URLs, preserving each independent discovery channel."""
    docs = {}
    for item in (existing or {}).get("items", []):
        url = item.get("url")
        if not url:
            continue
        try:
            key = canonical_url_hint(url)
        except ValueError:
            continue
        docs[key] = {"url": key, "publisher_host": urlsplit(key).hostname,
                     "existing_source_ids": item.get("source_ids", []),
                     "social_mentions": [], "discovery_channels": ["existing_catalogue"],
                     "review_status": "unreviewed", "validation": "not_assessed"}
    for post in posts:
        post_url = post.get("url")
        if not post_url:
            continue
        author = post.get("author_url") or post.get("author") or ""
        for url in external_links(post):
            entry = docs.setdefault(url, {"url": url, "publisher_host": urlsplit(url).hostname,
                "existing_source_ids": [], "social_mentions": [],
                "discovery_channels": [], "review_status": "unreviewed",
                "validation": "not_assessed"})
            if "mastodon" not in entry["discovery_channels"]:
                entry["discovery_channels"].append("mastodon")
            if not any(x["post_url"] == post_url for x in entry["social_mentions"]):
                entry["social_mentions"].append({"post_url": post_url, "author": author,
                                                   "published_at": post.get("published_at")})
    for entry in docs.values():
        entry["distinct_social_accounts"] = len({x["author"] for x in entry["social_mentions"] if x["author"]})
        entry["attention_hint"] = "socially_discovered" if entry["social_mentions"] else "other_discovery"
        entry["independence"] = "not_assessed"
    return {"schema_version": 1, "documents": len(docs), "items": sorted(docs.values(), key=lambda x:x["url"]),
            "policy": "Source URLs are discovery candidates, not verified original publications. Preserve other channels."}
