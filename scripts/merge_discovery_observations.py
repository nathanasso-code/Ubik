#!/usr/bin/env python3
"""Merge heterogeneous discovery observations without losing provenance.

Canonical URL grouping is a deduplication hint, not evidence that the publishers
are independent or that two different URLs describe the same event.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid", "igshid"}


def canonical_url(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("Invalid document URL")
    params = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                    if not k.lower().startswith("utm_") and k.lower() not in TRACKING)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path or "/", urlencode(params), ""))


def merge_observations(inputs):
    records = defaultdict(list)
    invalid = []
    for name, observations in inputs:
        for index, item in enumerate(observations):
            try:
                key = canonical_url(item["url"])
                records[key].append({
                    "origin": name, "observation_id": item.get("id"),
                    "source_id": item.get("source_id"), "original_url": item.get("original_url"),
                    "observed_url": item["url"], "title": item.get("title"),
                    "published_raw": item.get("published_raw"),
                    "provenance": item.get("provenance"),
                })
            except (KeyError, ValueError, TypeError):
                invalid.append({"origin": name, "index": index})
    return {"schema_version": 1, "documents": [
        {"canonical_url_hint": key, "observations": records[key],
         "observation_count": len(records[key]), "independent_confirmation": "not_assessed"}
        for key in sorted(records)], "invalid_observations": invalid,
        "note": "URL normalization is heuristic; preserve all observations and never infer corroboration."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    loaded = []
    for path in args.inputs:
        data = json.loads(path.read_text(encoding="utf-8"))
        observations = data.get("observations", data.get("items", []))
        if not isinstance(observations, list):
            raise ValueError(f"Invalid observations in {path}")
        loaded.append((path.name, observations))
    result = merge_observations(loaded)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"documents": len(result["documents"]),
                      "invalid": len(result["invalid_observations"])}))


if __name__ == "__main__":
    main()
