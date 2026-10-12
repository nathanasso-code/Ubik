"""Offline review of the existing 30-source AI topic dossier.

Never turn an editorial source summary into an independently verified claim.
Posts are perspectives, not independent corroborations of their linked article.
"""
import hashlib
from urllib.parse import urlparse

def review_ai_topic(dossier, *, limit=10):
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be positive")
    topic = dossier.get("topic")
    if not isinstance(topic, str) or not topic:
        raise ValueError("topic missing")
    candidates, seen = [], set()
    for source in dossier.get("sources", []):
        url, title = source.get("url"), source.get("title")
        if not isinstance(url, str) or not isinstance(title, str) or not title.strip():
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or url in seen:
            continue
        seen.add(url)
        perspectives = []
        for post in source.get("posts") or []:
            post_url = post.get("url")
            if not isinstance(post_url, str) or urlparse(post_url).scheme != "https":
                continue
            perspectives.append({
                "url": post_url, "author": post.get("author"),
                "kind_as_labelled": post.get("kind"), "description_as_labelled": post.get("summary"),
                "verification": "not_assessed",
                "independent_confirmation": False,
            })
        candidate = {
            "issue_id": hashlib.sha256((topic+"\n"+url).encode()).hexdigest()[:20],
            "topic_id": topic, "topic_assignment": "inherited_from_dossier",
            "category_as_labelled": source.get("category"),
            "title_as_labelled": title,
            "question_candidate": "Quali evidenze sostengono o contestano: «"+title.rstrip("?! .")+"»?",
            "origin": {"url": url, "author_or_publisher_as_labelled": source.get("author"),
                       "primary_status": "not_assessed",
                       "editorial_summary_as_labelled": source.get("summary")},
            "external_perspectives": perspectives,
            "card": {"title": title, "summary": None, "status": "draft_review_required"},
            "controversy_detected": False, "controversy_status": "not_assessed",
            "event_grouping": "not_assessed", "publication": "blocked",
            "needs_review": ["topic_fit", "issue_vs_document", "primary_source",
                             "claim_evidence", "independence", "counterevidence"],
        }
        candidates.append(candidate)
    candidates.sort(key=lambda c: (-int(bool(c["external_perspectives"])),
                                   -len(c["external_perspectives"]), c["issue_id"]))
    return {"schema_version": 1, "topic_id": topic, "source_count": len(candidates),
            "candidate_count": min(limit, len(candidates)),
            "items": candidates[:limit], "no_llm_calls": True,
            "no_automatic_publication": True,
            "caveat": "Curated dossier is an editorial input, not a validated live discovery snapshot."}
