"""One week of the AI corpus through the cheap pipeline candidate (exploratory, costs measured).

  extraction  DeepSeek V4.1 Flash, frozen v5.1 prompt, title + text up to 6000 characters, one news item per item
  retrieval   E5-small, top 5 per event, soft nature penalty, cross-source only
  judgment    DeepSeek on every pair; Sonnet 5.5 re-judges pairs DeepSeek did not call distinct, only if the
              preflight estimate fits the remaining budget (otherwise the escalation count is reported)
  composition v5.2, origins from the registry (an outlet's feeds count once)
No reference exists for this week: the run measures volume and cost, not accuracy.
Runs only in the private corpus repository.

Usage: python -m ingestion.ubik_week_run SELECTION.json OUT_DIR
"""
import json
import os
import sys
import urllib.error
from collections import Counter
from pathlib import Path

from ingestion.ubik_cost_guard import SAFETY, UNIT_COST, OverBudget, preflight
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_monarch_v5_rejudge_core import candidates
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK, compose, parse
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL as SONNET
from ingestion.ubik_v51_prompts import load_prompt
from ingestion.ubik_v5_extraction_validator import validate_extraction

CEILING_USD = 1.00
FULL_CHARS = 6000
MAX_PAIRS = 3000


def main(selection_path, out_dir):
    sel = json.loads(Path(selection_path).read_text())
    items = sel["items"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ex_prompt, eh = load_prompt("extraction")
    judge_prompt, jh = load_prompt("pair_judge")
    out = {"kind": "exploratory week run, volume and cost only", "prompt_sha256": {"extraction": eh, "pair_judge": jh},
           "code_commit": os.getenv("UBIK_COMMIT"), "window": sel["window"],
           "items": [{k: v for k, v in i.items() if k != "text"} for i in items],
           "preflight": [], "errors": [], "sources": [], "judgments": [], "cost": {"extract": 0.0, "deepseek_judge": 0.0, "sonnet_judge": 0.0}}

    def save():
        (out_dir / "week-run.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    def spent():
        return sum(out["cost"].values())

    def guard():
        if spent() > CEILING_USD:
            out["status"] = "aborted_cost_ceiling"
            save()
            raise SystemExit("Cost ceiling exceeded")

    def refuse(exc):
        out["status"] = "refused_preflight"
        save()
        raise SystemExit(str(exc))

    try:
        preflight("extraction", SAFETY * UNIT_COST["extract:deepseek_per_article_full"] * len(items), CEILING_USD, out["preflight"])
    except OverBudget as exc:
        refuse(exc)
    for it in items:
        payload = {"source_id": it["item_id"], "news": [{"key": "n1", "title": it["title"], "summary": it["text"][:FULL_CHARS]}]}
        for attempt in (1, 2):
            try:
                raw, cost, _ = call(DEEPSEEK, ex_prompt, payload)
            except urllib.error.HTTPError as exc:
                out["errors"].append({"stage": "extract", "item": it["item_id"], "error": exc.read(500).decode("utf-8", "replace")})
                break
            out["cost"]["extract"] += cost
            guard()
            try:
                content = raw["choices"][0]["message"]["content"] or ""
                answer = json.loads(content.strip().removeprefix("```json").removesuffix("```").strip())
                validate_extraction(answer, payload)
            except Exception as exc:
                out["errors"].append({"stage": "extract", "item": it["item_id"], "attempt": attempt, "error": str(exc)[:200]})
                continue
            out["sources"].append({"source_id": it["item_id"], "origin": it["origin"], "kind": it["kind"], "answer": answer})
            break
        save()

    pairs, scores, events = candidates(out["sources"], k=5, soft_nature=True)
    out["events"] = len(events)
    out["candidate_pairs"] = len(pairs)
    try:
        if len(pairs) > MAX_PAIRS:
            raise OverBudget(f"{len(pairs)} pairs exceed MAX_PAIRS={MAX_PAIRS}")
        preflight("deepseek judge", SAFETY * UNIT_COST["judge:deepseek"] * len(pairs), CEILING_USD - spent(), out["preflight"])
    except OverBudget as exc:
        refuse(exc)

    def judge(left, right, model, key):
        for attempt in (1, 2):
            raw, cost, _ = call(model, judge_prompt, {"left": events[left], "right": events[right]})
            out["cost"][key] += cost
            guard()
            try:
                return parse(raw["choices"][0]["message"]["content"] or "")
            except (ValueError, KeyError, TypeError) as exc:
                out["errors"].append({"stage": key, "pair": [left, right], "attempt": attempt, "error": str(exc)[:200]})
        return {"decision": "uncertain", "direction": None, "reason": "invalid_after_retry", "detail_conflicts": []}

    for left, right in pairs:
        first = judge(left, right, DEEPSEEK, "deepseek_judge")
        out["judgments"].append({"left": left, "right": right, "similarity": scores[(left, right)], "deepseek": first, "result": first})
        if len(out["judgments"]) % 50 == 0:
            save()
    save()
    escalate = [j for j in out["judgments"] if j["deepseek"]["decision"] != "distinct"]
    out["escalation"] = {"pairs": len(escalate), "rate": round(len(escalate) / max(1, len(pairs)), 3),
                         "deepseek_decisions": Counter(j["deepseek"]["decision"] for j in out["judgments"])}
    try:
        preflight("sonnet escalation", SAFETY * UNIT_COST["judge:sonnet"] * len(escalate), CEILING_USD - spent(), out["preflight"])
        for j in escalate:
            j["sonnet"] = judge(j["left"], j["right"], SONNET, "sonnet_judge")
            j["result"] = j["sonnet"]
        out["escalation"]["ran"] = True
        out["escalation"]["sonnet_decisions"] = Counter(j["sonnet"]["decision"] for j in escalate)
    except OverBudget as exc:
        out["escalation"]["ran"] = False
        out["escalation"]["refused"] = str(exc)
    save()

    origin_of = {s["source_id"]: s["origin"] for s in out["sources"]}
    built = compose(out, events, out["judgments"], scores, origin_of=origin_of)
    comp = built["composition"]
    multi = [c for c in comp["cards"] if len(c["source_ids"]) > 1]
    out["composition_summary"] = {
        "cards": len(comp["cards"]), "multi_item_cards": len(multi),
        "multi_origin_cards": sum(len(c.get("independent_origin_ids", [])) > 1 for c in multi),
        "incidents": len(comp["incidents"]), "matrices": len(comp["matrices"]),
        "matrix_sizes": [len(m["cards"]) for m in comp["matrices"]],
        "topic_cards": len(comp["topic_cards"])}
    out["composition"] = built
    out["total_cost_usd"] = spent()
    out["status"] = "completed"
    save()
    print(json.dumps({"items": len(items), "extracted": len(out["sources"]), "events": len(events), "pairs": len(pairs),
                      "cost": out["cost"], "escalation": out["escalation"], "summary": out["composition_summary"]}, default=str))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
