"""v5.2 regression: recomposing the frozen Ukraine v5.1 judgments must give the published compositions.

With no origin map the output must match the stored one exactly; with an identity origin map (every source
its own outlet, as in the Ukraine corpus) only origin_verification may change. No model calls.
"""
import json
from pathlib import Path

from ingestion.ubik_ukraine_v51_judge import compose

RESULTS = Path(__file__).resolve().parent.parent / "docs" / "experiment-results" / "v5.1"


def strip(comp):
    return json.loads(json.dumps(comp).replace('"origin_verification": "registry"', '"origin_verification": "provisional"'))


def main():
    extraction = json.loads((RESULTS / "ukraine-v51-extraction.json").read_text())
    events = {s["source_id"] + ":" + e["id"]: e for s in extraction["sources"] for e in s["answer"]["events"]}
    pairs = json.loads((RESULTS / "ukraine-v51-candidate-pairs.json").read_text())["pairs"]
    scores = {(p["left"], p["right"]): p["similarity"] for p in pairs}
    identity = {s["source_id"]: s["source_id"] for s in extraction["sources"]}
    for arm in ("sonnet", "deepseek"):
        stored = json.loads((RESULTS / f"ukraine-v51-judge-{arm}.json").read_text())
        plain = compose(extraction, events, stored["judgments"], scores)
        assert plain["composition"] == stored["composition"], f"{arm}: composition changed without origin map"
        with_origins = compose(extraction, events, stored["judgments"], scores, origin_of=identity)
        assert strip(with_origins["composition"]["incidents"]) == stored["composition"]["incidents"], f"{arm}: identity origins changed incidents"
        print(arm, "unchanged:", len(stored["composition"]["matrices"]), "matrices,", len(stored["composition"]["incidents"]), "incidents")


if __name__ == "__main__":
    main()
