"""Offline expansion of monitored authors and source domains from a reviewed dossier.

Candidates only: a social mention is not an endorsement or permission to monitor.
No requests, subscriptions, account verification or production writes.
"""
from urllib.parse import urlsplit

def expand(dossier):
    authors, publishers = {}, {}
    for source in dossier.get("sources", []):
        url = source.get("url")
        if isinstance(url, str):
            parsed = urlsplit(url)
            if parsed.scheme == "https" and parsed.hostname:
                host = parsed.hostname.lower()
                entry = publishers.setdefault(host, {"hostname": host, "document_urls": set(),
                    "feed_url": None, "status": "discovery_candidate", "feed_verified": False})
                entry["document_urls"].add(url)
        for post in source.get("posts") or []:
            handle = post.get("author")
            link = post.get("url")
            if not isinstance(handle, str) or not isinstance(link, str):
                continue
            parsed = urlsplit(link)
            if parsed.scheme != "https" or parsed.hostname != "bsky.app" or "/post/" not in parsed.path:
                continue
            entry = authors.setdefault(handle.casefold(), {"handle": handle, "platform": "bluesky",
                "post_urls": set(), "status": "discovery_candidate",
                "independence_verified": False, "expertise_verified": False})
            entry["post_urls"].add(link)
    return {"schema_version": 1, "topic_id": dossier.get("topic"),
            "authors": [{**x, "post_urls": sorted(x["post_urls"])} for x in sorted(authors.values(), key=lambda v:v["handle"])],
            "publishers": [{**x, "document_urls": sorted(x["document_urls"])} for x in sorted(publishers.values(), key=lambda v:v["hostname"])],
            "policy": "Candidates only. Review relevance, consent/provider rules, feed availability, duplication and identity before adding to monitoring."}
