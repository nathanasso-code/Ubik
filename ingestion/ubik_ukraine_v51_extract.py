"""Ukraine v5.1 extraction: identical to v5 except the system prompt, read from the frozen file.

Only extraction runs here. No retrieval, no judge: the blind mapping is frozen before any judgment.
"""
import json
import os
import urllib.request
from pathlib import Path

from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL, verify_response, verify_records
from ingestion.ubik_v5_extraction_validator import validate_extraction
from ingestion.ubik_v51_prompts import load_prompt

ROOT = Path("data/ukraine-v51")


def post_hoc_checks(answer):
    """Checks the validator does not enforce; reported, never used to reject or repair."""
    keys = [a.get("news_key") for a in answer["assignments"]]
    flags = []
    if len(keys) != len(set(keys)):
        flags.append({"check": "duplicate_news_key", "keys": sorted({k for k in keys if keys.count(k) > 1})})
    for a in answer["assignments"]:
        if a.get("primary_event_id") is None and not a.get("context_only"):
            flags.append({"check": "null_primary_without_context_only", "news_key": a.get("news_key")})
        reacts = {r.get("event_id") for r in a.get("reacts_to", []) if isinstance(r, dict)}
        both = reacts & set(a.get("mentions", []))
        if both:
            flags.append({"check": "event_in_reacts_to_and_mentions", "news_key": a.get("news_key"), "events": sorted(both)})
    return flags


def main():
    if os.getenv("UBIK_LLM_MODEL") != EXPECTED_MODEL:
        raise RuntimeError("Explicit Sonnet model required")
    prompt, prompt_hash = load_prompt("extraction")
    ROOT.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / "v4-sonnet55.json").read_text())
    if data["model"] != EXPECTED_MODEL:
        raise RuntimeError("Baseline model mismatch")
    out = {"version": "v5.1", "model": EXPECTED_MODEL, "input_kind": "frozen_v4_titles_and_summaries",
           "input_artifact": "12591716174", "prompt_file": "prompts/v5.1/extraction.txt",
           "prompt_sha256": prompt_hash, "code_commit": os.getenv("GITHUB_SHA"),
           "sources": [], "usage": [], "errors": [], "post_hoc_flags": {}}

    def save():
        (ROOT / "v51-extraction.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))

    for source in data["sources"]:
        payload = {"source_id": source["source_id"], "news": source["news"]}
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps({"model": EXPECTED_MODEL,
                                 "messages": [{"role": "system", "content": prompt},
                                              {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
                                 "response_format": {"type": "json_object"}, "max_tokens": 6500}).encode(),
                headers={"Authorization": "Bearer " + os.environ["UBIK_LLM_API_KEY"], "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as response:
                raw = json.load(response)
            record = verify_response(raw, requested_model=EXPECTED_MODEL, stage="extract", source_id=source["source_id"])
            content = raw["choices"][0]["message"]["content"]
            out.setdefault("raw_responses", []).append({"source_id": source["source_id"], "content": content})
            answer = json.loads(content.strip().removeprefix("```json").removesuffix("```").strip())
            try:
                validate_extraction(answer, payload)
            except Exception:
                out.setdefault("rejected_responses", []).append(
                    {"source_id": source["source_id"], "answer": answer, "model_audit": record})
                raise
            out["sources"].append({"source_id": source["source_id"], "news": source["news"], "answer": answer})
            out["post_hoc_flags"][source["source_id"]] = post_hoc_checks(answer)
            out["usage"].append(record)
        except Exception as exc:
            out["errors"].append({"source_id": source["source_id"], "error": str(exc)[:500]})
            save()
            raise
        save()
    out["cost_audit"] = verify_records(out["usage"])
    if len(out["sources"]) != len(data["sources"]):
        raise RuntimeError("Incomplete extraction")
    save()
    print(json.dumps({"sources": len(out["sources"]),
                      "events": sum(len(s["answer"]["events"]) for s in out["sources"]),
                      "prompt_sha256": prompt_hash, "cost": out["cost_audit"],
                      "post_hoc_flags": {k: v for k, v in out["post_hoc_flags"].items() if v}}))


if __name__ == "__main__":
    main()
