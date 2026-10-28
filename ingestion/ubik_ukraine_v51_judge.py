"""Ukraine v5.1 stage 4: one judge arm on the frozen v5.1 pairs, then the unchanged v5 composition.

Usage: python -m ingestion.ubik_ukraine_v51_judge sonnet|deepseek
The judge sees only the two event records; never the reference or the blind mapping.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_monarch_v5_rejudge_core import cautious_groups
from ingestion.ubik_part_of_validator_v5 import resolve_part_of
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL as SONNET, verify_response
from ingestion.ubik_v51_prompts import load_prompt

RESULTS = Path("docs/experiment-results/v5.1")
FROZEN = {"ukraine-v51-extraction.json": "851cc8db1712d6851ab0521b2462ec62470657cbf83fd88e8ff06599d1917fd7",
          "ukraine-v51-candidate-pairs.json": "b91889731b0f66e18d40363f7cd21e6331c905d3ba748d5acc0d66d59a403e5d"}
EXTRACTION_COST = 0.10377
DEEPSEEK = "deepseek/deepseek-v4.1-flash-1017"
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["decision", "direction", "reason", "detail_conflicts"],
          "properties": {"decision": {"type": "string", "enum": ["equivalent", "distinct", "uncertain", "part_of"]},
                         "direction": {"type": ["string", "null"], "enum": ["left_part_of_right", "right_part_of_left", None]},
                         "reason": {"type": "string"},
                         "detail_conflicts": {"type": "array", "items": {"type": "string"}}}}
ARMS = {
    "sonnet": {"model": SONNET, "ceiling_usd": 1.00,
               "extra": {"response_format": {"type": "json_object"}}},
    "deepseek": {"model": DEEPSEEK, "ceiling_usd": 0.10,
                 "extra": {"provider": {"order": ["nebius/fp8"], "allow_fallbacks": False, "require_parameters": True},
                           "reasoning": {"enabled": False},
                           "response_format": {"type": "json_schema",
                                               "json_schema": {"name": "ubik_pair_judgment", "strict": True, "schema": SCHEMA}}}},
}


def frozen(name):
    raw = (RESULTS / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN[name]:
        raise RuntimeError(f"{name} differs from the frozen file")
    return json.loads(raw)


def parse(content):
    answer = json.loads(content.strip().removeprefix("```json").removesuffix("```").strip())
    if answer.get("decision") not in ("equivalent", "distinct", "uncertain", "part_of"):
        raise ValueError("invalid decision")
    if answer["decision"] == "part_of" and answer.get("direction") not in ("left_part_of_right", "right_part_of_left"):
        raise ValueError("invalid direction")
    if not isinstance(answer.get("reason"), str) or not isinstance(answer.get("detail_conflicts"), list):
        raise ValueError("invalid reason or detail_conflicts")
    return answer


def compose(extraction, events, judgments, scores):
    """Identical to the v5 Ukraine composition path (cautious groups, relations, part_of check, composer)."""
    assembly = cautious_groups(events, judgments, scores)
    lookup = {e: "card:" + g[0] for g in assembly["groups"] for e in g}
    cards = [{"id": "card:" + g[0], "events": g, "source_ids": sorted({e.split(":")[0] for e in g})} for g in assembly["groups"]]
    relations = []
    for s in extraction["sources"]:
        sid = s["source_id"]
        for e in s["answer"]["events"]:
            for rel in e.get("event_part_of", []):
                a, b = lookup[sid + ":" + e["id"]], lookup[sid + ":" + rel["event_id"]]
                if a != b:
                    relations.append({"type": "part_of", "source": a, "target": b, "origin": sid + ":" + e["id"], "evidence": rel["evidence"]})
        for a in s["answer"]["assignments"]:
            p = a.get("primary_event_id")
            if p:
                for t in a.get("reacts_to", []):
                    x, y = lookup[sid + ":" + p], lookup[sid + ":" + t["event_id"]]
                    if x != y:
                        relations.append({"type": "reacts_to", "source": x, "target": y, "origin": sid + ":" + a["news_key"]})
    for j in assembly["part_of"]:
        a, b = j["left"], j["right"]
        child, parent = (a, b) if j["result"]["direction"] == "left_part_of_right" else (b, a)
        x, y = lookup[child], lookup[parent]
        if x != y:
            relations.append({"type": "part_of", "source": x, "target": y, "origin": "judge:" + a + "|" + b, "evidence": j["result"].get("reason", "")})
    accepted, rejected = resolve_part_of([r for r in relations if r["type"] == "part_of"])
    relations = [r for r in relations if r["type"] == "reacts_to"] + accepted
    return {"assembly": assembly, "relations": relations, "quarantined_relations": rejected,
            "composition": compose_connected_v5(cards, relations, conflicts=rejected)}


def main(arm_name):
    arm = ARMS[arm_name]
    prompt, prompt_hash = load_prompt("pair_judge")
    extraction = frozen("ukraine-v51-extraction.json")
    pairs_file = frozen("ukraine-v51-candidate-pairs.json")
    events = {s["source_id"] + ":" + e["id"]: e for s in extraction["sources"] for e in s["answer"]["events"]}
    pairs = [(p["left"], p["right"]) for p in pairs_file["pairs"]]
    scores = {(p["left"], p["right"]): p["similarity"] for p in pairs_file["pairs"]}
    out = {"version": "v5.1", "arm": arm_name, "model": arm["model"], "prompt_file": "prompts/v5.1/pair_judge.txt",
           "prompt_sha256": prompt_hash, "frozen_inputs": FROZEN, "code_commit": os.getenv("GITHUB_SHA"),
           "request_options": arm["extra"], "candidate_pairs": len(pairs), "judgments": [], "raw_responses": [],
           "usage": [], "errors": [], "invalid_after_retry": []}
    path = RESULTS / f"ukraine-v51-judge-{arm_name}.json"

    def save():
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")

    spent = 0.0
    for left, right in pairs:
        for attempt in (1, 2):
            body = {"model": arm["model"], "max_tokens": 3000,
                    "messages": [{"role": "system", "content": prompt},
                                 {"role": "user", "content": json.dumps({"left": events[left], "right": events[right]}, ensure_ascii=False)}]}
            body.update(arm["extra"])
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                         headers={"Authorization": "Bearer " + os.environ["UBIK_LLM_API_KEY"], "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=240) as resp:
                    raw = json.load(resp)
            except urllib.error.HTTPError as exc:
                out["errors"].append({"pair": [left, right], "attempt": attempt, "type": "http", "error": exc.read(2000).decode("utf-8", "replace")})
                save()
                raise
            usage = raw.get("usage", {})
            cost = usage.get("cost")
            out["usage"].append({"pair": [left, right], "attempt": attempt, "model": raw.get("model"), "provider": raw.get("provider"),
                                 "usage": usage, "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                                 "cost_usd": cost})
            if arm_name == "sonnet":
                verify_response(raw, stage="judge", pair=[left, right])
            elif raw.get("model") != DEEPSEEK or (raw.get("provider") and "nebius" not in raw["provider"].lower()):
                raise RuntimeError("Model or provider identity mismatch; abort")
            if not isinstance(cost, (int, float)):
                raise RuntimeError("Unreported cost; abort instead of counting zero")
            spent += cost
            if spent > arm["ceiling_usd"]:
                out["status"] = "aborted_cost_ceiling"
                save()
                raise SystemExit("Cost ceiling exceeded")
            content = raw["choices"][0]["message"]["content"]
            out["raw_responses"].append({"pair": [left, right], "attempt": attempt, "content": content})
            try:
                answer = parse(content)
            except (ValueError, KeyError, TypeError) as exc:
                out["errors"].append({"pair": [left, right], "attempt": attempt, "type": "invalid_response", "error": str(exc)[:200]})
                if attempt == 2:
                    out["invalid_after_retry"].append([left, right])
                    out["judgments"].append({"left": left, "right": right, "similarity": scores[(left, right)],
                                             "result": {"decision": "uncertain", "direction": None, "reason": "invalid_after_retry",
                                                        "detail_conflicts": [], "invalid_after_retry": True}})
                save()
                continue
            out["judgments"].append({"left": left, "right": right, "similarity": scores[(left, right)], "result": answer})
            save()
            break
    out["total_cost_usd"] = spent
    out["total_pipeline_cost_usd"] = EXTRACTION_COST + spent
    limit = max(1, int(0.05 * len(pairs)))
    out["status"] = "partial" if len(out["invalid_after_retry"]) > limit else "completed_unadjudicated"
    out.update(compose(extraction, events, out["judgments"], scores))
    save()
    c = out["composition"]
    print(json.dumps({"arm": arm_name, "status": out["status"], "pairs": len(out["judgments"]),
                      "invalid_after_retry": len(out["invalid_after_retry"]), "cost": spent,
                      "incidents": len(c["incidents"]), "matrices": len(c["matrices"])}))


if __name__ == "__main__":
    main(sys.argv[1])
