"""Deterministic detection of probable shared textual origin; not proof of agency syndication."""
import re
from collections import Counter

def words(s):
    return re.findall(r"[a-z0-9]+",s.lower())

def fingerprints(text, width=9):
    w=words(text)
    return {tuple(w[i:i+width]) for i in range(max(0,len(w)-width+1))}

def probable_shared_origin(source_a,source_b,min_shared_shingles=4,width=9):
    matches=[]
    for a in source_a["news"]:
        for b in source_b["news"]:
            a_text=" ".join(a.get("evidence_excerpts") or [])
            b_text=" ".join(b.get("evidence_excerpts") or [])
            if not a_text or not b_text:continue
            shared=fingerprints(a_text,width)&fingerprints(b_text,width)
            if len(shared)>=min_shared_shingles:
                matches.append({"left_news":a["key"],"right_news":b["key"],
                                "shared_shingles":len(shared)})
    return {"probable_common_origin":bool(matches),"evidence_pairs":matches,
            "method":"identical_9_token_shingles",
            "caution":"text reuse does not establish the actual originating publisher"}
