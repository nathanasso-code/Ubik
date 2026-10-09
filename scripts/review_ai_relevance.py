#!/usr/bin/env python3
"""Conservative AI relevance review for cross-disciplinary RSS metadata.

A lexical queue is NOT a classifier of truth, quality, or editorial importance.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

TERMS = {
    "direct": [r"\b(?:artificial intelligence|generative ai|genai|machine learning|deep learning|large language models?|llms?|chatgpt|openai|deepmind|intelligenza artificiale|apprendimento automatico|modelli linguistici|ia generativa|inteligencia artificial|intelligence artificielle|künstliche intelligenz|人工知能|人工智能)\b"],
    "context": [r"\b(?:automation|automazione|automatizzazione|productivity|produttivit[aà]|labor market|mercato del lavoro|employment|occupazione|neuroscience|neuroscienze|consciousness|coscienza|cognition|cognizione|algorithmic|algoritmic[oa]|economia digitale)\b"]
}

def normalize(text):
    return unicodedata.normalize("NFKC", str(text or "")).casefold()

def assess(item):
    title = normalize(item.get("title"))
    direct = any(re.search(p, title) for p in TERMS["direct"])
    contextual = any(re.search(p, title) for p in TERMS["context"])
    # Only title is available; never treat a contextual word as proof of AI relevance.
    status = "likely_ai" if direct else ("review_context" if contextual else "unknown")
    return {"id": item.get("id"), "source_id": item.get("source_id"), "url": item.get("url"),
            "title": item.get("title"), "language": item.get("language"),
            "relevance_status": status, "basis": "title_keywords_only",
            "original_authors": item.get("authors", []), "attribution_basis": item.get("attribution_basis")}

def review(discovery):
    rows = [assess(item) for item in discovery.get("items", [])]
    counts = {s: sum(x["relevance_status"] == s for x in rows) for s in ("likely_ai", "review_context", "unknown")}
    return {"schema_version": 1, "not_for_publication": True, "counts": counts, "items": rows}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    data = review(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Relevance review:", data["counts"])
