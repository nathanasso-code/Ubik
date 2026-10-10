#!/usr/bin/env python3
"""Metadata-only RSS/Atom discovery pilot. No LLM, scraping or automatic publication."""
import argparse
import datetime as dt
import hashlib
import html
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
DC = "{http://purl.org/dc/elements/1.1/}"
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

def summary_text(value):
    """Plain text preview of feed-provided markup; never fetch article body here."""
    value = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return clean(html.unescape(value))[:1800]

def attribution_type(authors, basis):
    if not authors:
        return "not_specified_in_feed"
    institutional = ("team", "staff", "redazione", "editorial", "newsroom", "research", "laboratory", "lab", "press", "communications")
    if all(any(token in name.casefold() for token in institutional) for name in authors):
        return "collective_or_institutional_candidate"
    return "named_in_feed"

def author_info(node, atom=False, fallback=None):
    """Keep authorship separate from publisher; never infer a person from a brand."""
    if atom:
        names = [text(a, ATOM + "name") for a in node.findall(ATOM + "author")]
        names = [name for name in names if name]
        if not names and fallback is not None:
            names = [text(a, ATOM + "name") for a in fallback.findall(ATOM + "author")]
            names = [name for name in names if name]
        return names, "entry" if node.findall(ATOM + "author") and names else ("feed" if names else "missing")
    names = [clean("".join(a.itertext())) for a in node.findall(DC + "creator")]
    if names:
        return [name for name in names if name], "entry"
    # RSS author often contains an email address; do not publish personal email as a byline.
    raw = text(node, "author")
    match = re.search(r"\(([^()]+)\)\s*$", raw)
    return ([match.group(1).strip()] if match else []), ("entry" if match else "missing")

def parse_feed(data, source):
    root = ET.fromstring(data)
    items = []
    if root.tag == ATOM + "feed":
        for entry in root.findall(ATOM + "entry"):
            link = next((x.get("href") for x in entry.findall(ATOM + "link") if x.get("rel", "alternate") == "alternate" and x.get("href")), None)
            items.append((text(entry, ATOM+"title"), link, text(entry, ATOM+"id"), text(entry, ATOM+"published") or text(entry, ATOM+"updated"), *author_info(entry, True, root), summary_text(text(entry, ATOM+"summary") or text(entry, ATOM+"content"))))
    else:
        channel = root.find("channel")
        if channel is None:
            raise ValueError("Unsupported feed format")
        for item in channel.findall("item"):
            items.append((text(item, "title"), text(item, "link"), text(item, "guid"), text(item, "pubDate"), *author_info(item), summary_text(text(item, "description") or text(item, CONTENT+"encoded"))))
    results = []
    for title, link, guid, published, authors, attribution_basis, summary in items:
        url = canonical(link)
        if not title or not url:
            continue
        key = hashlib.sha256((source["id"] + "|" + (guid or url)).encode()).hexdigest()[:24]
        results.append({"id": key, "source_id": source["id"], "publisher": source["name"], "authors": authors, "attribution_basis": attribution_basis, "attribution_type": attribution_type(authors, attribution_basis), "attribution_status": "feed_only_unverified", "description": summary, "description_basis": "feed", "original_url": link, "discovered_from": source.get("url"), "title": title[:500], "url": url, "external_id": guid or None, "published_raw": published or None, "topic_ids": ["ai-models"], "status": "discovered"})
    return results

def raw_feed_entry_count(data):
    """Count upstream RSS/Atom entries before normalization and URL validation."""
    root = ET.fromstring(data)
    if root.tag == ATOM + "feed":
        return len(root.findall(ATOM + "entry"))
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Unsupported feed format")
    return len(channel.findall("item"))


def run(registry, output, fetch):
    config = json.loads(registry.read_text(encoding="utf-8"))
    if config.get("topic_id") != "ai-models":
        raise ValueError("Unexpected topic")
    previous = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {"items": []}
    # Preserve provenance for each source, even when multiple feeds link to one URL.
    items = {(item["source_id"], item["url"]): item for item in previous.get("items", [])}
    reports = []
    for source in config["sources"]:
        if not source.get("enabled") or source.get("kind") != "rss":
            continue
        try:
            payload = fetch(source["url"])
            raw_entries = raw_feed_entry_count(payload)
            discovered = parse_feed(payload, source)
            new = 0
            for item in discovered:
                key = (item["source_id"], item["url"])
                if key not in items:
                    items[key] = item
                    new += 1
                elif not items[key].get("authors") and item["authors"]:
                    items[key].update({"authors": item["authors"], "attribution_basis": item["attribution_basis"], "attribution_type": item["attribution_type"], "attribution_status": item["attribution_status"]})
                if item.get("description") and not items[key].get("description"):
                    items[key].update({"description": item["description"], "description_basis": "feed"})
            reports.append({"source_id": source["id"], "status": "ok", "raw_entries": raw_entries, "seen": len(discovered), "new": new})
        except (ValueError, ET.ParseError, urllib.error.URLError, TimeoutError, OSError) as exc:
            reports.append({"source_id": source["id"], "status": "error", "error": str(exc)[:240]})
    source_stats = []
    for report in reports:
        source_items = [item for item in items.values() if item["source_id"] == report["source_id"]]
        count = len(source_items)
        source_stats.append({**report,
            "stored": count,
            "with_named_author": sum(bool(item.get("authors")) for item in source_items),
            "missing_named_author": sum(not bool(item.get("authors")) for item in source_items),
            "with_publication_date": sum(bool(item.get("published_raw")) for item in source_items),
            "with_original_link": sum(bool(item.get("original_url")) for item in source_items)})
    result = {"schema_version": 1, "topic_id": "ai-models", "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(), "items": sorted(items.values(), key=lambda x: x["id"]), "source_reports": source_stats, "coverage": {"enabled_feeds": len(reports), "successful_feeds": sum(r["status"] == "ok" for r in reports), "failed_feeds": sum(r["status"] == "error" for r in reports), "stored_items": len(items), "unique_article_urls": len({item["url"] for item in items.values()}), "items_with_named_author": sum(bool(item.get("authors")) for item in items.values()), "items_missing_named_author": sum(not bool(item.get("authors")) for item in items.values()), "items_with_publication_date": sum(bool(item.get("published_raw")) for item in items.values())}}
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
