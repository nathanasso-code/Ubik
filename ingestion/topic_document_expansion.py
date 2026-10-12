"""Document-led query expansion from *observed* repeated URL slug terms.

A term is eligible only if multiple distinct observed accounts link to
documents whose URL slugs contain it. Generic topic terms are excluded.
This deliberately makes no claim about semantic entity recognition.
"""
from collections import defaultdict
from .topic_event_candidates import slug_tokens, STOP

def propose_document_terms(records,seed_terms=(),*,min_accounts=2,max_terms=6):
    if not 2<=min_accounts<=20 or not 1<=max_terms<=20:
        raise ValueError("Invalid discovery budget")
    excluded=set(STOP)
    for term in seed_terms:
        excluded.update(term.casefold().split())
    groups=defaultdict(lambda:{"accounts":set(),"posts":set(),"documents":set()})
    for record in records:
        meta=record.get("metadata") or {}
        for url in set(meta.get("linked_documents") or []):
            for token in slug_tokens(url):
                if token in excluded or len(token)>40:
                    continue
                g=groups[token]
                g["accounts"].add(record["source_id"])
                g["posts"].add(record["url"])
                g["documents"].add(url)
    out=[]
    for token,g in groups.items():
        if len(g["accounts"])<min_accounts or len(g["documents"])<2:
            continue
        out.append({"term":token,"accounts_observed":len(g["accounts"]),
                    "documents_observed":len(g["documents"]),
                    "supporting_posts":sorted(g["posts"])[:12],
                    "supporting_documents":sorted(g["documents"])[:12],
                    "discovery_basis":"repeated_url_slug_token"})
    out.sort(key=lambda x:(-x["accounts_observed"],-x["documents_observed"],x["term"]))
    return out[:max_terms]
