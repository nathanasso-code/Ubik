"""Ukraine v5.1 stage 3: candidate pairs with the unchanged v5 retrieval, frozen before any judgment."""
import hashlib
import json
from pathlib import Path

from ingestion.ubik_monarch_v5_rejudge_core import candidates

RESULTS = Path("docs/experiment-results/v5.1")
EXTRACTION = RESULTS / "ukraine-v51-extraction.json"
EXPECTED_EXTRACTION_SHA256 = "851cc8db1712d6851ab0521b2462ec62470657cbf83fd88e8ff06599d1917fd7"


def main():
    raw = EXTRACTION.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_EXTRACTION_SHA256:
        raise RuntimeError("Extraction differs from the frozen file")
    extraction = json.loads(raw)
    pairs, scores, events = candidates(extraction["sources"], k=5, soft_nature=True)
    out = {"version": "v5.1", "stage": "candidate pairs, frozen before any judgment",
           "extraction_sha256": EXPECTED_EXTRACTION_SHA256,
           "retrieval": {"model": "intfloat/multilingual-e5-small", "text": "passage: action + object",
                         "k": 5, "soft_nature": True, "nature_penalty": 0.08, "cross_source_only": True,
                         "dedup": "unordered pair, max similarity", "order": "similarity desc, then id"},
           "events": len(events), "candidate_pairs": len(pairs),
           "pairs": [{"left": a, "right": b, "similarity": scores[(a, b)]} for a, b in pairs]}
    (RESULTS / "ukraine-v51-candidate-pairs.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"events": len(events), "candidate_pairs": len(pairs)}))


if __name__ == "__main__":
    main()
