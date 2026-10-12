"""Evidence-led hashtag expansion, independent of any expected event.

Only co-occurring tags observed from seed results are eligible. The expansion
budget is fixed before collection. Every candidate carries supporting post URLs.
"""
import re
from collections import defaultdict

TAG = re.compile(r"(?<!\w)#([\w]{3,48})",re.UNICODE)
GENERIC = {"news","breaking","world","politics","update","updates","media",
           "notizie","actualité","новости","новина","viral","trending"}

def observed_hashtags(records):
    groups=defaultdict(lambda: {"accounts":set(),"posts":set(),"providers":set()})
    for record in records:
        meta=record.get("metadata") or {}
        tags=set(str(x).lstrip("#").casefold() for x in meta.get("hashtags",[]) if isinstance(x,str))
        tags.update(x.casefold() for x in TAG.findall(meta.get("text_preview") or record.get("title") or ""))
        for tag in tags:
            if tag not in GENERIC:
                row=groups[tag]
                row["accounts"].add(record["source_id"])
                row["posts"].add(record["url"])
                row["providers"].add(record["connector"])
    return groups

def propose_expansion(records, seed_terms, *, min_accounts=2, max_terms=8):
    if not 1<=max_terms<=30 or not 2<=min_accounts<=20:
        raise ValueError("Invalid expansion budget")
    seed={re.sub(r"[^\w]","",x).casefold() for x in seed_terms}
    proposals=[]
    for tag,row in observed_hashtags(records).items():
        if tag in seed or len(row["accounts"])<min_accounts:
            continue
        proposals.append({"term":tag,"independent_accounts_unverified":len(row["accounts"]),
                          "post_count":len(row["posts"]),
                          "supporting_posts":sorted(row["posts"])[:12],
                          "providers":sorted(row["providers"]),
                          "discovery_basis":"observed_cooccurring_hashtag"})
    proposals.sort(key=lambda x:(-x["independent_accounts_unverified"],
                                  -x["post_count"],x["term"]))
    return proposals[:max_terms]
