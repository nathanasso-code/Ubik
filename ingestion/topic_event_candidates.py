"""Conservative, auditable event grouping from discovered external URLs.

No predetermined event names or search terms. This is candidate grouping,
not a factual assertion that documents describe the same event.
"""
import re
from collections import defaultdict
from urllib.parse import urlsplit, unquote

STOP={"news","article","articles","world","worldnews","live","updates","update","latest",
      "today","yesterday","october","2026","2025","2024","2023","2022","html","amp",
      "ukraine","russia","russian","ukrainian","war","guerra","ucraina","russia",
      "notizie","novosti","the","and","for","with","from","about","that","this",
      "della","delle","degli","sulla","sulle","sono","alla","nella","dopo","per",
      "video","breaking","report","reports","politics","politica","newsfeed"}
def slug_tokens(url):
    path=unquote(urlsplit(url).path).casefold()
    terms=re.findall(r"[^\W_]+",path,flags=re.UNICODE)
    return set(t for t in terms if len(t)>=4 and not t.isdecimal() and t not in STOP)

def group_document_candidates(documents,min_shared=2,threshold=0.42):
    """Group only with >=2 shared distinctive tokens and Jaccard >= threshold.

    This favors precision over recall; multilingual equivalents are not resolved.
    """
    if not 0<threshold<=1:
        raise ValueError("Invalid threshold")
    parent=list(range(len(documents)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    toks=[slug_tokens(d["url"]) for d in documents]
    for i in range(len(documents)):
        for j in range(i):
            a,b=toks[i],toks[j]
            if len(a&b)<min_shared:
                continue
            score=len(a&b)/len(a|b) if a|b else 0
            if score>=threshold:
                parent[root(i)]=root(j)
    groups=defaultdict(list)
    for i,d in enumerate(documents):
        groups[root(i)].append(d)
    out=[]
    for members in groups.values():
        posts=set(p for d in members for p in d.get("post_urls",[]))
        out.append({"documents":members,"document_count":len(members),
                    "post_count":len(posts),
                    "post_urls":sorted(posts),
                    "status":"candidate_unverified",
                    "method":"url_slug_token_overlap"})
    out.sort(key=lambda g:(-g["document_count"],-g["post_count"],
                           g["documents"][0]["url"]))
    return out
