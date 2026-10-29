"""Exploratory v5.1 probe on collected corpus items (articles and social posts). Not a measurement.

Each selected item is treated as one source with one news item (title + text, truncated). Runs the
frozen v5.1 extraction and pair-judge prompts with Sonnet 5.5, the v5 retrieval and the v5 composition,
and checks whether a post's reaction lands on the event of the article it links to.

Declared deviations from the v5.1 Ukraine protocol: input is full article text or a social post, not a
title-and-summary news item; one news item per source; no blind reference. Results must run and stay in
the private corpus repository, because inputs contain full texts.

Usage: python -m ingestion.ubik_corpus_probe_v51 SELECTION.json OUT_DIR
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

from ingestion.ubik_monarch_v5_rejudge_core import candidates
from ingestion.ubik_ukraine_v51_judge import compose, parse
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL, verify_response
from ingestion.ubik_v51_prompts import load_prompt
from ingestion.ubik_v5_extraction_validator import validate_extraction

CEILING_USD = 1.50
MAX_CHARS = 6000


def call(system, user, max_tokens):
    body = {"model": EXPECTED_MODEL, "max_tokens": max_tokens, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + os.environ["UBIK_LLM_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as resp:
        raw = json.load(resp)
    verify_response(raw, stage="probe")
    return raw


def main(selection_path, out_dir):
    selection = json.loads(Path(selection_path).read_text())
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    extraction_prompt, eh = load_prompt("extraction")
    judge_prompt, jh = load_prompt("pair_judge")
    out = {"kind": "exploratory probe, not a measurement", "model": EXPECTED_MODEL,
           "prompt_sha256": {"extraction": eh, "pair_judge": jh}, "selection": selection_path,
           "sources": [], "raw": [], "errors": [], "judgments": [], "cost_usd": 0.0}

    def save():
        (out_dir / "probe-result.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    def spend(raw):
        out["cost_usd"] += float((raw.get("usage") or {}).get("cost") or 0)
        if out["cost_usd"] > CEILING_USD:
            out["status"] = "aborted_cost_ceiling"
            save()
            raise SystemExit("Cost ceiling exceeded")

    for item in selection["items"]:
        sid = item["probe_id"]
        payload = {"source_id": sid, "news": [{"key": "n1", "title": item.get("title") or "",
                                                "summary": (item.get("text") or "")[:MAX_CHARS]}]}
        try:
            raw = call(extraction_prompt, json.dumps(payload, ensure_ascii=False), 6500)
            spend(raw)
            content = raw["choices"][0]["message"]["content"]
            out["raw"].append({"stage": "extract", "source_id": sid, "content": content})
            answer = json.loads(content.strip().removeprefix("```json").removesuffix("```").strip())
            validate_extraction(answer, payload)
            out["sources"].append({"source_id": sid, "news": payload["news"], "answer": answer,
                                   "kind": item["kind"], "publisher": item.get("publisher"), "corpus_id": item["corpus_id"], "url": item["url"],
                                   "links_to": item.get("links_to")})
        except SystemExit:
            raise
        except Exception as exc:
            out["errors"].append({"stage": "extract", "source_id": sid, "error": str(exc)[:300]})
        save()

    pairs, scores, events = candidates(out["sources"], k=5, soft_nature=True)
    out["candidate_pairs"] = len(pairs)
    for left, right in pairs:
        try:
            raw = call(judge_prompt, json.dumps({"left": events[left], "right": events[right]}, ensure_ascii=False), 3000)
            spend(raw)
            answer = parse(raw["choices"][0]["message"]["content"])
            out["judgments"].append({"left": left, "right": right, "similarity": scores[(left, right)], "result": answer})
        except SystemExit:
            raise
        except Exception as exc:
            out["errors"].append({"stage": "judge", "pair": [left, right], "error": str(exc)[:300]})
        save()

    built = compose(out, events, out["judgments"], scores)
    out.update(built)
    by_sid = {s["source_id"]: s for s in out["sources"]}
    lookup = {e: "card:" + g[0] for g in built["assembly"]["groups"] for e in g}
    checks = []
    for s in out["sources"]:
        target = s.get("links_to")
        if not target or target not in by_sid:
            continue
        reacts = [r["event_id"] for a in s["answer"]["assignments"] for r in a.get("reacts_to", [])]
        mentions = [m for a in s["answer"]["assignments"] for m in a.get("mentions", [])]
        own_events = [s["source_id"] + ":" + e for e in reacts + mentions]
        article_primary = [target + ":" + a["primary_event_id"] for a in by_sid[target]["answer"]["assignments"] if a.get("primary_event_id")]
        linked = any(lookup.get(o) == lookup.get(p) for o in own_events for p in article_primary)
        same_incident = any(set(built["composition"]["memberships"].get(lookup.get(s["source_id"] + ":" + a["primary_event_id"], ""), []))
                            & set(built["composition"]["memberships"].get(lookup.get(p, ""), []))
                            for a in s["answer"]["assignments"] if a.get("primary_event_id") for p in article_primary)
        checks.append({"post": s["source_id"], "article": target, "post_reacts_to": reacts, "post_mentions": mentions,
                       "referent_matched_article_event": linked, "post_in_article_incident": same_incident})
    out["link_checks"] = checks
    out["cards_by_probe_item"] = {s["source_id"]: sorted({lookup.get(s["source_id"] + ":" + e["id"]) for e in s["answer"]["events"]})
                                  for s in out["sources"]}
    out["multi_item_cards"] = [{"card": "card:" + g[0], "items": sorted({e.split(":")[0] for e in g}),
                                "publishers": sorted({by_sid[e.split(":")[0]].get("publisher") for e in g})}
                               for g in built["assembly"]["groups"] if len({e.split(":")[0] for e in g}) > 1]
    out["status"] = "completed"
    save()
    print(json.dumps({"sources": len(out["sources"]), "pairs": len(pairs), "cost": round(out["cost_usd"], 4),
                      "errors": len(out["errors"]), "link_checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
