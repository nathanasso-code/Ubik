"""Conservative cross-query deduplication of public Mastodon observations.

This module does not assess truth, topic relevance, or independence of sources.
It preserves discovery provenance without storing status text.
"""
import json
from collections import defaultdict
from pathlib import Path


def merge_discoveries(pages):
    """Merge pages by ActivityPub URI, retaining all discovery paths."""
    grouped = {}
    warnings = []
    for page in pages:
        if page.get("connector") != "mastodon":
            raise ValueError("Expected Mastodon discovery page")
        warnings.append(page.get("coverage_warning", "Instance-visible coverage only"))
        for record in page.get("observations", []):
            if record.get("connector") != "mastodon":
                raise ValueError("Expected Mastodon observation")
            key = record.get("external_id")
            if not isinstance(key, str) or not key.startswith("https://"):
                raise ValueError("Missing ActivityPub URI")
            origin = record.get("discovered_from")
            if key not in grouped:
                merged = dict(record)
                merged["metadata"] = dict(record.get("metadata") or {})
                merged["discovered_via"] = [origin] if origin else []
                merged["alternate_urls"] = []
                grouped[key] = merged
            else:
                merged = grouped[key]
                if origin and origin not in merged["discovered_via"]:
                    merged["discovered_via"].append(origin)
                url = record.get("url")
                if url and url != merged.get("url") and url not in merged["alternate_urls"]:
                    merged["alternate_urls"].append(url)
                tags = merged["metadata"].get("tags", [])
                for tag in (record.get("metadata") or {}).get("tags", []):
                    if tag not in tags:
                        tags.append(tag)
                merged["metadata"]["tags"] = tags
    return {
        "schema_version": 1,
        "connector": "mastodon",
        "observations": list(grouped.values()),
        "raw_observation_count": sum(len(p.get("observations", [])) for p in pages),
        "unique_observation_count": len(grouped),
        "coverage_warning": "Only discovered instance-visible public posts; not a Fediverse census.",
        "editorial_status": "unassessed",
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pages", nargs="+", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    pages = [json.loads(path.read_text(encoding="utf-8")) for path in args.pages]
    merged = merge_discoveries(pages)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"raw": merged["raw_observation_count"],
                      "unique": merged["unique_observation_count"]}))


if __name__ == "__main__":
    main()
