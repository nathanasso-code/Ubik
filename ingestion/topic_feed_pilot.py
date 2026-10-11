"""Review-only, low-cost AI topic feed selection from existing RSS metadata.

Conservative: distinct documents stay separate unless independently reviewed.
No LLM costs, no claim-level extraction, no automatic epistemic validation.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

TOPIC = {
    "id": "ai-models",
    "name": "Modelli e sistemi di intelligenza artificiale",
    "matrix": "Intelligenza artificiale",
    "areas": ["modelli-e-capacita", "ricerca-e-valutazione",
              "rilasci-e-prodotti", "sicurezza-e-governance",
              "impatto-economico-sociale"],
}
TERMS = {
    "modelli-e-capacita": ["llm", "language model", "foundation model", "multimodal",
                           "reasoning model", "transformer", "model weights"],
    "ricerca-e-valutazione": ["benchmark", "arxiv", "research", "paper", "evaluation", "dataset"],
    "rilasci-e-prodotti": ["release", "launched", "announced", "api", "open source", "released"],
    "sicurezza-e-governance": ["alignment", "safety", "regulation", "governance", "risk"],
    "impatto-economico-sociale": ["employment", "labor", "jobs", "economy", "education", "society"],
}
AI_TERMS = (" ai ", "artificial intelligence", "machine learning", " llm", "language model",
            "gpt-", "chatgpt", "deepmind", "neural network", "generative ai", "openai",
            "claude", "gemini", "transformer")
STOP = {"with", "from", "that", "this", "about", "their", "model", "models",
        "artificial", "intelligence", "the", "and", "for", "new", "using", "into"}


def _date(raw):
    if not raw:
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            value = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def classify(item):
    body = " " + re.sub(r"\s+", " ", (item.get("title", "") + " " + item.get("description", "")).casefold()) + " "
    matched = [area for area, terms in TERMS.items() if any(term in body for term in terms)]
    explicit_ai = any(term in body for term in AI_TERMS)
    return matched, explicit_ai


def candidate_key(title):
    words = re.findall(r"[a-z0-9]+", title.casefold())
    return tuple(sorted(set(w for w in words if len(w) > 3 and w not in STOP)))


def select(discovery, *, limit=30, now=None):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be 1..100")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone aware")
    by_url = defaultdict(list)
    for item in discovery["items"]:
        by_url[item["url"]].append(item)
    candidates = []
    for url, observations in by_url.items():
        item = observations[0]
        areas, ai_explicit = classify(item)
        if not ai_explicit:
            continue
        published = _date(item.get("published_raw"))
        age_days = (now - published).total_seconds() / 86400 if published else None
        if age_days is not None and (age_days < -1 or age_days > 14):
            continue
        # Transparent metadata-only heuristics, not credibility/quality scores.
        sources = sorted({x["source_id"] for x in observations})
        candidates.append({
            "url": url, "title": item["title"], "source_ids": sources,
            "publisher": item.get("publisher"), "authors": item.get("authors", []),
            "published_raw": item.get("published_raw"), "area_ids": areas,
            "same_document_observations": len(observations),
            "message_extraction": "not_available_metadata_only",
            "source_quality": "not_assessed",
            "same_event": "unverified",
            "trend": "not_measured",
            "display_kind": "standalone_source_candidate",
            "_published": published.timestamp() if published else float("-inf"),
        })
    # Newest first, with source round-robin to prevent one high-volume publisher
    # monopolizing the display. This is NOT a popularity or relevance ranking.
    by_source = defaultdict(list)
    for row in candidates:
        by_source[row["source_ids"][0]].append(row)
    for rows in by_source.values():
        rows.sort(key=lambda x: (-x["_published"], x["url"]))
    chosen = []
    while len(chosen) < limit and any(by_source.values()):
        for source in sorted(by_source):
            if by_source[source] and len(chosen) < limit:
                chosen.append(by_source[source].pop(0))
    for row in candidates:
        row.pop("_published")
    return {
        "schema_version": 1, "topic": TOPIC, "feed_limit": limit,
        "candidate_documents": len(candidates), "all_candidates": candidates, "visible": chosen,
        "excluded_or_older": len(by_url) - len(candidates),
        "review_required_for_event_merges": True,
        "automatic_nuclei": False, "automatic_publication": False,
        "trend_estimation": "unavailable_without_time_series",
        "method": "explicit AI keywords, 14-day window, per-source balanced recent sample",
        "limitations": [
            "Keyword matches may miss relevant stories or include false positives.",
            "No full-text claim extraction, semantic similarity or source credibility scoring.",
            "Same URL deduplicated; same-event distinct URLs not merged automatically.",
            "Cross-source corroboration requires origin-dependency review.",
            "No historic time series to identify actual trends.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("discovery", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    result = select(json.loads(args.discovery.read_text(encoding="utf-8")), limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": result["candidate_documents"], "visible": len(result["visible"])}))


if __name__ == "__main__":
    main()
