"""Offline federation of source snapshots into one auditable ingestion manifest."""
import argparse
import json
from pathlib import Path

from .legacy_adapters import hacker_news_to_observation, rss_to_observation
from .contracts import canonical_url_hint


def normalize_snapshot(snapshot):
    connector = snapshot.get("connector")
    if connector == "hacker_news_newstories":
        return [hacker_news_to_observation(x) for x in snapshot.get("observations", [])]
    if connector == "gdelt_doc":
        return snapshot.get("observations", [])
    if isinstance(snapshot.get("items"), list):
        return [rss_to_observation(x) for x in snapshot["items"]]
    raise ValueError("Unknown discovery snapshot type")


def federate(named_snapshots):
    observations, errors = [], []
    for name, snapshot in named_snapshots:
        try:
            normalized = normalize_snapshot(snapshot)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"source_file": name, "error": type(exc).__name__})
            continue
        for index, item in enumerate(normalized):
            try:
                hint = canonical_url_hint(item["url"])
                if not isinstance(item.get("connector"), str) or not isinstance(item.get("source_id"), str):
                    raise ValueError("Missing source identity")
                observations.append({**item, "canonical_url_hint": hint, "snapshot": name})
            except (ValueError, KeyError, TypeError) as exc:
                errors.append({"source_file": name, "index": index, "error": type(exc).__name__})
    sources = sorted({(x["connector"], x["source_id"]) for x in observations})
    urls = {x["canonical_url_hint"] for x in observations}
    return {
        "schema_version": 1,
        "purpose": "unselected_federated_acquisition",
        "observations": observations,
        "metrics": {
            "observations": len(observations),
            "distinct_url_hints": len(urls),
            "duplicate_url_observations": len(observations) - len(urls),
            "connector_source_pairs": len(sources),
            "source_pairs": [{"connector": a, "source_id": b} for a, b in sources],
            "errors": len(errors),
        },
        "errors": errors,
        "selection_applied": False,
        "clustering_applied": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = [(str(path), json.loads(path.read_text(encoding="utf-8"))) for path in args.inputs]
    result = federate(inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["metrics"], ensure_ascii=False))


if __name__ == "__main__":
    main()
