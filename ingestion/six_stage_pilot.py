"""Six-stage, evidence-preserving Ubik pilot from already acquired feed metadata.

No paid APIs, no automatic publication, no fabricated external mention counts.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from ingestion.topic_evidence import evidence
from ingestion.topic_event_review import tokens


def fingerprint(url):
    parts = urlsplit(url or "")
    host = (parts.hostname or "").lower().removeprefix("www.")
    if host in {"arxiv.org", "export.arxiv.org"}:
        match = re.search(r"/(?:abs|pdf)/(\d{4}\.\d+)", parts.path)
        if match:
            return "arxiv:" + match.group(1)
    if host == "doi.org":
        return "doi:" + parts.path.strip("/").lower()
    return None


def message(row):
    note = evidence(row)
    description = (row.get("description") or "").strip()
    if note["description_evidence"]:
        central = note["description_evidence"][0]
        basis = "feed_description_verbatim"
    elif description:
        central = description[:500]
        basis = "feed_description_excerpt"
    else:
        central = None
        basis = "title_only"
    url = row.get("url", "")
    if "arxiv.org/abs/" in url:
        kind = "preprint_author_claim"
    elif any(x in url for x in ("openai.com/", "deepmind.google/")):
        kind = "institutional_claim"
    else:
        kind = "source_report_or_opinion_unclassified"
    return {
        "url": url, "title": row.get("title"), "authors": row.get("authors", []),
        "publisher": row.get("publisher"), "published_raw": row.get("published_raw"),
        "source_ids": row.get("source_ids", []), "central_message": central,
        "message_basis": basis, "claim_type_candidate": kind,
        "full_text_accessed": False, "verified_claim": False,
        "review_status": "unreviewed",
    }


def pipeline(catalog, *, limit=300):
    rows = catalog.get("items", [])
    selected = [r for r in rows if r.get("relevance_hint") == "explicit_ai_signal"][:limit]
    messages = [message(r) for r in selected]
    refs = defaultdict(list)
    for row in rows:
        key = fingerprint(row.get("url"))
        if key:
            refs[key].append(row["url"])
    relevance = []
    for row in selected:
        key = fingerprint(row["url"])
        same_document = sorted(set(refs.get(key, []))) if key else [row["url"]]
        relevance.append({
            "url": row["url"], "external_mentions": None,
            "external_mentions_status": "not_measured",
            "internal_same_work_links": same_document,
            "independent_web_origins": None, "social_mentions": None,
            "ranking_status": "not_rankable_without_web_evidence",
            "search_queries": [row["url"], '"' + (row.get("title") or "")[:150] + '"'],
        })
    # Fase 4: safe standalone cards; suggestions are never auto-merged.
    cards = [{"card_id": "source-" + str(i+1), "title": r["title"],
              "summary": r["central_message"], "summary_basis": r["message_basis"],
              "source_urls": [r["url"]], "card_status": "standalone_unverified",
              "auto_merged": False} for i, r in enumerate(messages)]
    proposed = []
    for i, left in enumerate(selected):
        a = tokens(left.get("title"))
        for j in range(i+1, len(selected)):
            right = selected[j]
            if set(left.get("source_ids", [])) & set(right.get("source_ids", [])):
                continue
            shared = a & tokens(right.get("title"))
            if len(shared) >= 3:
                proposed.append({"left": left["url"], "right": right["url"],
                                 "shared_title_terms": sorted(shared),
                                 "status": "candidate_not_same_event_verified"})
                if len(proposed) >= 50:
                    break
        if len(proposed) >= 50:
            break
    # Fase 5: explicit search queue; a URL is a target, not a discovered comment.
    social = [{"source_url": r["url"], "queries": ['"' + r["url"] + '"',
               '"' + (r.get("title") or "")[:120] + '"'],
               "verified_social_references": [], "status": "pending_public_search"}
              for r in selected[:30]]
    # Fase 6: never suppress sources with no external evidence.
    long_tail = [{"url": r["url"], "title": r["title"],
                  "reason": "No verified external reference measurement yet",
                  "citation_search": [r["url"], fingerprint(r["url"])],
                  "status": "needs_citation_search"}
                 for r in selected]
    return {
        "schema_version": 1, "scope": "review_only_no_paid_apis",
        "phase1": {"acquired_documents": len(rows), "selected_for_processing": len(selected),
                   "continual_refresh": "existing scheduled discovery workflow"},
        "phase2": {"messages": messages},
        "phase3": {"relevance_evidence": relevance, "ranked_documents": [],
                   "reason": "No live external web citation corpus ingested; never infer counts"},
        "phase4": {"cards": cards, "possible_relations": proposed,
                   "verified_merges": 0},
        "phase5": {"public_discussion_search_queue": social,
                   "verified_discussions": 0},
        "phase6": {"long_tail_review_queue": long_tail,
                   "excluded_for_low_popularity": 0},
        "no_automatic_publication": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=300)
    args = parser.parse_args()
    report = pipeline(json.loads(args.catalog.read_text(encoding="utf-8")), limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"processed": len(report["phase2"]["messages"]),
                      "cards": len(report["phase4"]["cards"]),
                      "proposed_relations": len(report["phase4"]["possible_relations"]),
                      "verified_external_mentions": 0, "automatic_merges": 0}))


if __name__ == "__main__":
    main()
