#!/usr/bin/env python3
"""Metadata-only RSS/Atom discovery pilot. No LLM, scraping or automatic publication."""
import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/source-registry.ai-models.json"
OUTPUT = ROOT / "data/discovery/ai-models.json"
ATOM = "{http://www.w3.org/2005/Atom}"
CONTENT = "{http://purl.org/rss/1.0/modules/content/}"

def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()

def canonical(url):
    parsed = urllib.parse.urlsplit((url or "").strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if not (k.lower().startswith("utm_") or k.lower() in {"fbclid", "gclid"})]
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", urllib.parse.urlencode(query), ""))

def text(node, tag):
    el = node.find(tag)
    return clean("".join(el.itertext())) if el is not None else ""

def parse_feed(data, source):
    root = ET.fromstring(data)
    items = []
    if root.tag == ATOM + "feed":
        for entry in root.findall(ATOM + "entry"):
            link = next((x.get("href") for x in entry.findall(ATOM + "link") if x.get("rel", "alternate") == "alternate" and x.get("href")), None)
            items.append((text(entry, ATOM+"title"), link, text(entry, ATOM+"id"), text(entry, ATOM+"published") or text(entry, ATOM+"updated")))
    else:
        channel = root.find("channel")
        if channel is None:
            raise ValueError("Unsupported feed format")
        for item in channel.findall("item"):
            items.append((text(item, "title"), text(item, "link"), text(item, "guid"), text(item, "pubDate")))
    results = []
    for title, link, guid, published in items:
        url = canonical(link)
        if not title or not url:
            continue
        key = hashlib.sha256((source["id"] + "|" + (guid or url)).encode()).hexdigest()[:24]
        results.append({"id": key, "source_id": source["id"], "publisher": source["name"], "title": title[:500], "url": url, "external_id": guid or None, "published_raw": published or None, "topic_ids": ["ai-models"], "status": "discovered"})
    return results

def run(registry, output, fetch):
    config = json.loads(registry.read_text(encoding="utf-8"))
    if config.get("topic_id") != "ai-models":
        raise ValueError("Unexpected topic")
    previous = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {"items": []}
    items = {item["url"]: item for item in previous.get("items", [])}
    reports = []
    for source in config["sources"]:
        if not source.get("enabled") or source.get("kind") != "rss":
            continue
        try:
            payload = fetch(source["url"])
            discovered = parse_feed(payload, source)
            new = 0
            for item in discovered:
                if item["url"] not in items:
                    items[item["url"]] = item
                    new += 1
            reports.append({"source_id": source["id"], "status": "ok", "seen": len(discovered), "new": new})
        except (ValueError, ET.ParseError, urllib.error.URLError, TimeoutError, OSError) as exc:
            reports.append({"source_id": source["id"], "status": "error", "error": str(exc)[:240]})
    result = {"schema_version": 1, "topic_id": "ai-models", "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(), "items": sorted(items.values(), key=lambda x: x["id"]), "source_reports": reports}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "UbikDiscoveryPilot/0.1 (metadata only)", "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=20) as response:
        if int(response.headers.get("Content-Length", "0")) > 3_000_000:
            raise ValueError("Feed exceeds limit")
        data = response.read(3_000_001)
        if len(data) > 3_000_000:
            raise ValueError("Feed exceeds limit")
        return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = run(args.registry, args.output, fetch)
    print(json.dumps({"total": len(result["items"]), "sources": result["source_reports"]}, ensure_ascii=False))
