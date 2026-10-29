"""Extraction cost pilot (preregistered: protocols/ubik-extraction-cost-pilot.md).

Arms on the same articles, frozen v5.1 extraction prompt, one news item per article:
  S-full  Sonnet 5.5, title + text up to 6000 characters (current configuration)
  D-full  DeepSeek V4.1 Flash (Nebius FP8, no reasoning), same input
  D-lede  DeepSeek V4.1 Flash, title + first ~1500 characters
Then E5 coverage: for every S-full event, best cosine to any event of the other arm on the same article.
Runs only in the private corpus repository (inputs are full texts).

Usage: python -m ingestion.ubik_extraction_pilot SELECTION.json OUT_DIR
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from ingestion.ubik_cost_guard import OverBudget, UNIT_COST, extraction_estimate, preflight
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL as SONNET
from ingestion.ubik_v51_prompts import load_prompt
from ingestion.ubik_v5_extraction_validator import validate_extraction

CEILING_USD = 0.45
FULL_CHARS = 6000
LEDE_CHARS = 1500
DEEPSEEK_EXTRA = {"provider": {"order": ["nebius/fp8"], "allow_fallbacks": False, "require_parameters": True},
                  "reasoning": {"enabled": False}, "response_format": {"type": "json_object"}}
ARMS = {"S-full": (SONNET, FULL_CHARS), "D-full": (DEEPSEEK, FULL_CHARS), "D-lede": (DEEPSEEK, LEDE_CHARS)}


def lede(text, limit):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    stop = max(cut.rfind(". "), cut.rfind(".\n"))
    return cut[:stop + 1] if stop > limit // 2 else cut


def call(model, prompt, payload):
    body = {"model": model, "max_tokens": 6500,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]}
    body.update(DEEPSEEK_EXTRA if model == DEEPSEEK else {"response_format": {"type": "json_object"}})
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + os.environ["UBIK_LLM_API_KEY"], "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = json.load(resp)
    if raw.get("model") != model or (model == DEEPSEEK and raw.get("provider") and "nebius" not in raw["provider"].lower()):
        raise RuntimeError(f"Model or provider mismatch: {raw.get('model')} / {raw.get('provider')}")
    cost = (raw.get("usage") or {}).get("cost")
    if not isinstance(cost, (int, float)):
        raise RuntimeError("Unreported cost; abort instead of counting zero")
    return raw, cost, round(time.time() - t0, 1)


def coverage(results, items):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")

    def text(e):
        return "passage: " + str(e.get("action") or "") + " " + str(e.get("object") or "")
    out = {}
    for arm in ("D-full", "D-lede"):
        rows = []
        for it in items:
            base = results["S-full"].get(it["item_id"])
            other = results[arm].get(it["item_id"])
            if not base or not other or not base["events"] or not other["events"]:
                continue
            a = model.encode([text(e) for e in base["events"]], normalize_embeddings=True)
            b = model.encode([text(e) for e in other["events"]], normalize_embeddings=True)
            sims = (a @ b.T).max(axis=1)
            for e, s in zip(base["events"], sims):
                rows.append({"item": it["item_id"], "event": e["id"], "text_role": e["text_role"],
                             "is_primary": e["id"] == base["primary"], "best_sim": round(float(s), 3)})
        summary = {}
        for t in (0.88, 0.90):
            for role in ("narrated", "referenced"):
                sel = [r for r in rows if r["text_role"] == role]
                summary[f"{role}@{t}"] = [sum(r["best_sim"] >= t for r in sel), len(sel)]
            prim = [r for r in rows if r["is_primary"]]
            summary[f"primary@{t}"] = [sum(r["best_sim"] >= t for r in prim), len(prim)]
        out[arm] = {"summary": summary, "rows": rows}
    return out


def main(selection_path, out_dir):
    sel = json.loads(Path(selection_path).read_text())
    items = sel["items"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt, prompt_hash = load_prompt("extraction")
    out = {"protocol": "protocols/ubik-extraction-cost-pilot.md", "prompt_sha256": prompt_hash, "code_commit": os.getenv("UBIK_COMMIT"),
           "selection": {"seed": sel["seed"], "window": sel["window"], "items": [{k: v for k, v in i.items() if k != "text"} for i in items]},
           "preflight": [], "calls": [], "errors": [], "results": {a: {} for a in ARMS}, "cost_by_arm": {a: 0.0 for a in ARMS}}

    def save():
        (out_dir / "extraction-pilot.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    chars = sum(min(len(i["text"]), FULL_CHARS) for i in items)
    sonnet_est = extraction_estimate(chars, len(items))
    # DeepSeek per-call cost relative to Sonnet, measured on the Ukraine judges (about 1/20); two DeepSeek arms.
    deepseek_est = 2 * sonnet_est * UNIT_COST["judge:deepseek"] / UNIT_COST["judge:sonnet"]
    try:
        preflight("extraction pilot, three arms", sonnet_est + deepseek_est, CEILING_USD, out["preflight"])
    except OverBudget as exc:
        out["status"] = "refused_preflight"
        save()
        raise SystemExit(str(exc))
    spent = 0.0
    for it in items:
        for arm, (model, limit) in ARMS.items():
            text = it["text"][:limit] if limit == FULL_CHARS else lede(it["text"], limit)
            payload = {"source_id": it["item_id"], "news": [{"key": "n1", "title": it["title"], "summary": text}]}
            for attempt in (1, 2):
                try:
                    raw, cost, secs = call(model, prompt, payload)
                except urllib.error.HTTPError as exc:
                    out["errors"].append({"arm": arm, "item": it["item_id"], "attempt": attempt, "type": "http",
                                          "error": exc.read(1000).decode("utf-8", "replace")})
                    save()
                    break
                spent += cost
                out["cost_by_arm"][arm] += cost
                u = raw.get("usage") or {}
                out["calls"].append({"arm": arm, "item": it["item_id"], "attempt": attempt, "cost_usd": cost, "seconds": secs,
                                     "prompt_tokens": u.get("prompt_tokens"), "completion_tokens": u.get("completion_tokens"),
                                     "input_chars": len(text)})
                if spent > CEILING_USD:
                    out["status"] = "aborted_cost_ceiling"
                    save()
                    raise SystemExit("Cost ceiling exceeded")
                content = raw["choices"][0]["message"]["content"] or ""
                try:
                    answer = json.loads(content.strip().removeprefix("```json").removesuffix("```").strip())
                    validate_extraction(answer, payload)
                except Exception as exc:
                    out["errors"].append({"arm": arm, "item": it["item_id"], "attempt": attempt, "type": "invalid", "error": str(exc)[:300],
                                          "content_head": content[:300]})
                    save()
                    continue
                a = answer["assignments"][0]
                out["results"][arm][it["item_id"]] = {"events": answer["events"], "primary": a.get("primary_event_id"),
                                                      "reacts_to": [r["event_id"] for r in a.get("reacts_to", [])],
                                                      "mentions": a.get("mentions", []), "context_only": a.get("context_only")}
                save()
                break
    out["total_cost_usd"] = spent
    out["coverage_vs_S_full"] = coverage(out["results"], items)
    out["status"] = "completed"
    save()
    print(json.dumps({"cost_by_arm": out["cost_by_arm"], "valid": {a: len(r) for a, r in out["results"].items()},
                      "errors": len(out["errors"]), "coverage": {a: v["summary"] for a, v in out["coverage_vs_S_full"].items()}}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
