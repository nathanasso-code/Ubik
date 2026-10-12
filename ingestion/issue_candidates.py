"""Conservative, offline issue candidates from existing topic evidence records.

No LLM, web calls, automatic clustering, or publication. A candidate remains
one document unless a reviewer explicitly links other evidence.
"""
from urllib.parse import urlparse
import hashlib
import re

def _words(value):
    return set(re.findall(r"[a-z0-9]{3,}", (value or "").casefold()))

def propose_issues(evidence_report, *, topic_id=None, limit=10):
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be positive integer")
    topic = topic_id or evidence_report.get("topic_id")
    if not topic:
        raise ValueError("topic_id is required")
    seen = set()
    items = []
    for record in evidence_report.get("items", []):
        url = record.get("url")
        title = (record.get("title") or "").strip()
        if not url or not title or url in seen:
            continue
        seen.add(url)
        if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
            continue
        excerpts = [x for x in (record.get("description_evidence") or []) if isinstance(x, str) and x.strip()]
        basis = "feed_description_verbatim" if excerpts else "title_only"
        words = _words(title)
        question = "Quali elementi documentano o contestano: «" + title.rstrip(".?!") + "»?"
        issue_id = hashlib.sha256((topic + "\n" + url).encode()).hexdigest()[:20]
        items.append({
            "issue_id": issue_id, "topic_id": topic, "topic_status": "inherited_candidate",
            "question": question,
            "trigger_observation_ids": [],
            "card": {"title": title, "summary": None, "status": "draft_insufficient_evidence"},
            "claims": [],
            "sources": [{
                "url": url, "role": "unclassified", "primary_status": "unverified",
                "origin_observation_ids": [], "verbatim_excerpts": excerpts[:2],
                "evidence_basis": basis,
            }],
            "missing_evidence": [
                "Independent source verification", "Primary source classification",
                "Claim-level support and counterevidence", "Human topic and issue review"
            ],
            "research_queries": [title],
            "review_required": True,
            "publication": "blocked",
            "quality_flags": {
                "has_description": bool(excerpts),
                "candidate_terms": len(words),
                "event_identity": "not_assessed",
                "controversy": "not_assessed",
            },
        })
    # Prioritize candidates with actual excerpts; avoid pretending controversy detection.
    items.sort(key=lambda x: (-int(x["quality_flags"]["has_description"]),
                              -x["quality_flags"]["candidate_terms"], x["issue_id"]))
    return {
        "schema_version": 1, "topic_id": topic, "candidate_count": len(items),
        "visible_count": min(limit, len(items)), "items": items[:limit],
        "method": "single-document conservative issue seeds; no semantic event grouping",
        "no_llm_calls": True, "no_automatic_publication": True,
    }
