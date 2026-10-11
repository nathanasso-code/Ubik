"""Extractive, zero-LLM-cost evidence notes from already acquired feed metadata.

Never paraphrase source claims or infer that a claim has been verified.
"""
import argparse
import json
import re
from pathlib import Path

CLAIM_MARKERS = ("find", "found", "show", "suggest", "report", "propos", "argu",
                 "demonstrat", "evaluat", "introduc", "announc", "releas", "claim")
TYPES = {
    "research_candidate": ("arxiv.org/abs/", "nber.org/papers/"),
    "opinion_or_analysis_candidate": ("normaltech.ai/p/", "interconnects.ai/p/"),
}


def _sentences(value):
    value = re.sub(r"\s+", " ", value or "").strip()
    # Split conservatively; preserve the exact wording of extracted spans.
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", value) if x.strip()]


def evidence(item):
    title = (item.get("title") or "").strip()
    description = (item.get("description") or "").strip()
    sentences = _sentences(description)
    substantive = [s for s in sentences if len(s) >= 65]
    preferred = [s for s in substantive if any(x in s.casefold() for x in CLAIM_MARKERS)]
    selected = (preferred or substantive)[:2]
    url = item.get("url") or ""
    content_type = "unclassified"
    for name, hosts in TYPES.items():
        if any(host in url for host in hosts):
            content_type = name
            break
    if content_type == "unclassified" and any(x in title.casefold() for x in ("benchmark", "study:", "evaluating")):
        content_type = "research_candidate"
    return {
        "url": url, "title": title, "source_ids": item.get("source_ids", []),
        "publisher": item.get("publisher"), "area_ids": item.get("area_ids", []),
        "content_type_candidate": content_type,
        "title_evidence": title,
        "description_evidence": selected,
        "description_available": bool(description),
        "description_characters": len(description),
        "evidence_basis": "feed_description_verbatim" if selected else "title_only",
        "message_status": "extractive_unverified" if selected else "insufficient_text",
        "full_text_accessed": False,
        "claim_verified": False,
        "editorial_decision": "review_required",
    }


def build(discovery, topic_report):
    # Join only by exact canonical URL, preserving the original feed summary.
    original = {}
    for item in discovery.get("items", []):
        original.setdefault(item.get("url"), item)
    candidates = topic_report.get("all_candidates", topic_report.get("visible", []))
    results = []
    for row in candidates:
        source = original.get(row.get("url"), {})
        results.append(evidence({**row, "description": source.get("description", "")}))
    return {
        "schema_version": 1,
        "topic_id": topic_report.get("topic", {}).get("id"),
        "candidate_count": len(results),
        "with_description_evidence": sum(bool(x["description_evidence"]) for x in results),
        "title_only": sum(not bool(x["description_evidence"]) for x in results),
        "items": results,
        "method": "verbatim extractive evidence from existing RSS/Atom descriptions",
        "no_llm_calls": True,
        "no_automatic_publication": True,
        "caveats": [
            "Feed summaries can be truncated, promotional or absent.",
            "Extracted text is attributed source language, not a validated factual claim.",
            "Content type is only a weak candidate label; review before use.",
            "No full article text, causal relation or event identity inferred.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("discovery", type=Path)
    parser.add_argument("topic_report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = build(json.loads(args.discovery.read_text(encoding="utf-8")),
                   json.loads(args.topic_report.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"evidence_candidates": result["candidate_count"],
                      "with_description_evidence": result["with_description_evidence"],
                      "title_only": result["title_only"]}))


if __name__ == "__main__":
    main()
