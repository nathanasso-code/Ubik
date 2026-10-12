"""Conservative, review-only event PAIR proposals from global RSS snapshots.

Never merges events, assigns topics or infers article claims. Uses title tokens,
document frequency, publication proximity and distinct publisher hosts.
"""
import argparse
import json
import math
import re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit

STOP=set("""about above after again against along also among around before behind being
between could during every first following found from have into just latest
more most news other over says said some than that their there these this those
through today under update updates what when where which while with would
world report reports video live watch breaking exclusive analysis opinion government discusses
the and for are was were has had its new
della delle degli nella sulla sono anche come dopo alla negli delle
alla agli allo degli della delle nelle dagli sulla questa questo
""".split())

def tokens(title):
    return {t for t in re.findall(r"[^\W_]+",str(title or "").casefold(),re.UNICODE)
            if len(t)>=4 and t not in STOP and not t.isdecimal()}

def published(raw):
    if not raw:return None
    try:
        d=datetime.fromisoformat(raw.replace("Z","+00:00"))
    except (ValueError,AttributeError):
        try:d=parsedate_to_datetime(raw)
        except (ValueError,TypeError):return None
    return (d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d).astimezone(timezone.utc)

def event_pair_candidates(snapshot,*,min_shared=2,min_similarity=0.44,max_hours=72,limit=100):
    if not 2<=min_shared<=8 or not 0<min_similarity<=1 or not 1<=max_hours<=336 or not 1<=limit<=500:
        raise ValueError("Invalid pair proposal budget")
    docs={}
    for item in snapshot.get("items",[]):
        url=item.get("url")
        if not isinstance(url,str) or urlsplit(url).scheme not in ("http","https"):continue
        title=item.get("title") or ""
        if not tokens(title):continue
        row={"url":url,"title":title,"source_id":item.get("source_id"),
             "host":urlsplit(url).hostname or "",
             "published_raw":item.get("published_raw")}
        docs.setdefault(url,row)
    rows=list(docs.values())
    df=Counter(t for row in rows for t in tokens(row["title"]))
    # Avoid full quadratic pair comparisons: inverted index, with a per-term
    # cap to prevent ubiquitous names/words from generating huge candidate sets.
    inverted=defaultdict(list)
    for i,row in enumerate(rows):
        for t in tokens(row["title"]):
            if df[t]<=max(12,int(len(rows)*0.16)):
                inverted[t].append(i)
    shared=Counter()
    for indices in inverted.values():
        for pair in combinations(indices,2):shared[pair]+=1
    results=[]
    for (i,j),count in shared.items():
        if count<min_shared:continue
        a,b=rows[i],rows[j]
        if a["host"]==b["host"]:continue
        da,db=published(a["published_raw"]),published(b["published_raw"])
        if da is None or db is None:continue
        hours=abs((da-db).total_seconds())/3600
        if hours>max_hours:continue
        ta,tb=tokens(a["title"]),tokens(b["title"])
        common=ta&tb
        weights={t:math.log((len(rows)+1)/(df[t]+1))+1 for t in ta|tb}
        numerator=sum(weights[t] for t in common)
        denominator=sum(weights[t] for t in ta|tb)
        score=round(numerator/denominator,4) if denominator else 0
        if score<min_similarity:continue
        results.append({"documents":[a,b],"shared_title_terms":sorted(common),
                        "weighted_title_jaccard":score,"publication_gap_hours":round(hours,1),
                        "status":"requires_human_same_event_review",
                        "same_event_verified":False})
    results.sort(key=lambda x:(-x["weighted_title_jaccard"],x["publication_gap_hours"],
                               x["documents"][0]["url"]))
    return {"schema_version":1,"purpose":"global_event_pair_review_only",
            "documents_considered":len(rows),"candidate_pairs":results[:limit],
            "candidate_pairs_before_limit":len(results),
            "automatic_event_merges":False,"topic_assignment_applied":False,
            "limitations":[
                "Title overlap can confuse related but distinct events; human review required.",
                "Cross-language paraphrases often remain undetected.",
                "Publication dates can be missing or unreliable.",
                "Different publisher hosts do not prove editorial independence.",
                "Candidate pairs are not fact checks or publishable summaries."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("snapshot",type=Path);p.add_argument("--output",required=True,type=Path)
    p.add_argument("--limit",type=int,default=100)
    a=p.parse_args()
    result=event_pair_candidates(json.loads(a.snapshot.read_text(encoding="utf-8")),limit=a.limit)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"documents":result["documents_considered"],
                      "review_pairs":len(result["candidate_pairs"]),
                      "total_candidates":result["candidate_pairs_before_limit"]}))
if __name__=="__main__":main()
