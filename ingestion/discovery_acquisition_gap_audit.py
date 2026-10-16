"""Offline audit separating discovery coverage from text acquisition coverage.

No HTTP calls, no LLM calls, no automatic publication. Consumes existing
global RSS snapshot and an optional acquired-document snapshot.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid"}

def canonical(url):
    try:
        p = urlsplit(url.strip())
        if p.scheme not in ("http", "https") or not p.hostname:
            return ""
        query = urlencode(sorted((k, v) for k, v in parse_qsl(p.query)
                                 if not k.lower().startswith("utm_") and k.lower() not in TRACKING))
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", query, ""))
    except ValueError:
        return ""

def text_of(doc):
    for key in ("full_text", "text", "body", "content", "abstract", "description", "summary"):
        val = doc.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip(), key
    return "", "none"

def audit(discovery, acquired, minimum_chars=800):
    if minimum_chars < 1:
        raise ValueError("minimum_chars must be positive")
    items = discovery.get("items", discovery.get("documents", []))
    docs = acquired.get("documents", acquired.get("items", []))
    found = {}
    for row in items:
        key = canonical(row.get("url", ""))
        if key:
            found.setdefault(key, []).append(row)
    bodies = {}
    for row in docs:
        key = canonical(row.get("url", ""))
        if key:
            txt, field = text_of(row)
            if key not in bodies or len(txt) > bodies[key]["chars"]:
                bodies[key] = {"chars": len(txt), "field": field}
    matched = set(found) & set(bodies)
    substantial = {u for u in matched if bodies[u]["chars"] >= minimum_chars}
    hosts = Counter(urlsplit(u).hostname for u in found)
    return {
        "schema_version": 1,
        "minimum_chars": minimum_chars,
        "discovery": {
            "observations": len(items),
            "unique_urls": len(found),
            "duplicate_observations": sum(len(v)-1 for v in found.values()),
            "domains": len(hosts),
            "top_domains": hosts.most_common(15),
            "source_reports": discovery.get("source_reports", []),
        },
        "acquisition": {
            "supplied_documents": len(docs),
            "discovered_urls_with_acquired_record": len(matched),
            "discovered_urls_without_acquired_record": len(set(found)-matched),
            "discovered_urls_with_800plus_chars": len(substantial),
            "discovered_urls_with_short_text": len(matched-substantial),
            "substantial_fraction_of_discovered": round(len(substantial)/len(found), 4) if found else None,
            "acquired_but_not_in_discovery": len(set(bodies)-set(found)),
            "examples_without_acquired_record": sorted(set(found)-matched)[:20],
            "examples_short_text": [{"url":u, **bodies[u]} for u in sorted(matched-substantial)[:20]],
        },
        "limitations": [
            "URLs absent from discovery cannot be counted without an independent reference set.",
            "Missing acquired record does not prove HTTP/parser failure: URL may never have been attempted.",
            "Character threshold is a triage signal, not proof of full text, legal reuse or semantic adequacy.",
            "URL normalization does not establish article identity across different canonical URLs.",
            "Acquired document field may contain only an abstract; provenance and content tier require separate checks.",
        ],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--acquired", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-chars", type=int, default=800)
    args = parser.parse_args()
    discovered = json.loads(args.discovery.read_text(encoding="utf-8"))
    acquired = json.loads(args.acquired.read_text(encoding="utf-8")) if args.acquired else {}
    result = audit(discovered, acquired, args.minimum_chars)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"discovery": {k:v for k,v in result["discovery"].items() if k not in ("source_reports","top_domains")},
                      "acquisition": {k:v for k,v in result["acquisition"].items() if not k.startswith("examples")}}))
if __name__ == "__main__":
    main()
