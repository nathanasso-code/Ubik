#!/usr/bin/env python3
"""Bounded audit of article-page bylines. No automatic publication or identity matching."""
import argparse
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import socket
import urllib.parse
import urllib.request

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = []
        self.scripts = []
        self.in_json = False
        self.json_buffer = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            if key in ("author", "article:author", "parsely-author", "dc.creator", "citation_author"):
                self.meta.append((key, a.get("content", "").strip()))
        if tag == "script" and "ld+json" in a.get("type", "").lower():
            self.in_json = True
            self.json_buffer = []
    def handle_data(self, data):
        if self.in_json:
            self.json_buffer.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self.in_json:
            self.scripts.append("".join(self.json_buffer))
            self.json_buffer = []
            self.in_json = False

def extract(page):
    p = Metadata()
    p.feed(page)
    findings = []
    for key, value in p.meta:
        if value:
            findings.append({"name": html.unescape(value), "kind": "unverified", "evidence": key})
    for script in p.scripts:
        try:
            obj = json.loads(script)
        except (ValueError, TypeError):
            continue
        def walk(node):
            if isinstance(node, list):
                for n in node:
                    yield from walk(n)
            elif isinstance(node, dict):
                types = node.get("@type", [])
                types = [types] if isinstance(types, str) else types
                if any(t in ("Article", "NewsArticle", "BlogPosting", "ScholarlyArticle") for t in types):
                    authors = node.get("author", [])
                    authors = authors if isinstance(authors, list) else [authors]
                    for author in authors:
                        if isinstance(author, str) and author.strip():
                            yield {"name": author.strip(), "kind": "unverified", "evidence": "jsonld:author"}
                        elif isinstance(author, dict) and author.get("name"):
                            typ = author.get("@type", "unknown")
                            yield {"name": author["name"], "kind": typ if typ in ("Person", "Organization") else "unverified", "evidence": "jsonld:author"}
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        yield from walk(value)
        findings.extend(walk(obj))
    return list({(x["name"], x["kind"], x["evidence"]): x for x in findings}.values())

def safe_url(url):
    parsed = urllib.parse.urlsplit(url or "")
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        return bool(addresses) and all(ipaddress.ip_address(info[4][0]).is_global for info in addresses)
    except (OSError, ValueError):
        return False

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Redirects disabled for bounded audit")

def fetch(url):
    if not safe_url(url):
        raise ValueError("Unsafe or unresolvable URL")
    request = urllib.request.Request(url, headers={"User-Agent": "UbikAttributionAudit/0.1", "Accept": "text/html"})
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(request, timeout=10) as response:
        if "html" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("Not HTML")
        payload = response.read(350_001)
        if len(payload) > 350_000:
            raise ValueError("Page exceeds audit limit")
        return payload.decode("utf-8", errors="replace")

def sample(items, limit):
    # Round-robin by source; no single large publisher dominates the audit.
    groups = {}
    for item in items:
        if (not item.get("authors") or item.get("attribution_basis") == "feed") and item.get("url", "").startswith("https://"):
            groups.setdefault(item.get("source_id", "unknown"), []).append(item)
    for group in groups.values():
        group.sort(key=lambda x: (x.get("published_raw") or "", x.get("url", "")), reverse=True)
    result = []
    while len(result) < limit and any(groups.values()):
        for key in sorted(groups):
            if groups[key] and len(result) < limit:
                result.append(groups[key].pop(0))
    return result

def audit(discovery, limit=24, fetcher=fetch):
    rows = []
    for item in sample(discovery.get("items", []), limit):
        try:
            found = extract(fetcher(item["url"]))
            status = "page_author_candidate" if found else "not_found_in_page_metadata"
            rows.append({"source_id": item["source_id"], "url": item["url"], "title": item["title"], "status": status, "candidates": found})
        except Exception as exc:
            rows.append({"source_id": item["source_id"], "url": item["url"], "title": item["title"], "status": "fetch_error", "error": str(exc)[:160]})
    return {"schema_version": 1, "sample_size": len(rows), "scope": "missing_or_inherited_feed_author", "publication_allowed": False, "results": rows}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=24)
    args = parser.parse_args()
    result = audit(json.loads(args.input.read_text(encoding="utf-8")), max(0, min(args.limit, 48)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Audited pages:", result["sample_size"])
