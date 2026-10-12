"""Blind, source-grounded relation discovery; no datacenter or topic seed.

A relation is only a co-mention hypothesis. Never infer causation, agreement,
contradiction or factual truth from shared title vocabulary.
"""
import argparse,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit

STOP=set("""about after again against amid among around before behind being between could would should there their these those where which while world report reports news latest update updates live video watch says said says over under from with into near this that have been were they them will more most than then other first found today yesterday tomorrow during since some many also major officials government people police president leader leaders trump breaking exclusive analysis opinion investigation explains scientists study studies research science journal article new year years day days country countries states state south north east west united international national local global shows reveal reveals makes made take takes told amid""".split())
def words(title):
    return [w for w in re.findall(r"[^\W_]+",str(title).casefold(),re.UNICODE)
            if len(w)>=5 and w not in STOP and not w.isdigit()]
def discover(snapshot,*,min_publishers=2,max_edges=35,max_terms_per_doc=18):
    docs={}
    for row in snapshot.get("items",[]):
        url=row.get("url");title=row.get("title")
        if not isinstance(url,str) or not isinstance(title,str):continue
        host=urlsplit(url).hostname
        if not host or urlsplit(url).scheme not in ("http","https"):continue
        if url not in docs:
            docs[url]={"url":url,"title":title,"host":host,"terms":set(words(title)[:max_terms_per_doc])}
    # Co-mentions are counted per distinct publisher host, not feed or repost.
    term_docs=defaultdict(set); term_hosts=defaultdict(set)
    for url,d in docs.items():
        for term in d["terms"]:
            term_docs[term].add(url);term_hosts[term].add(d["host"])
    valid={t for t,hosts in term_hosts.items() if len(hosts)>=min_publishers
           and len(term_docs[t])>=2 and len(term_docs[t])<=max(8,int(len(docs)*.12))}
    pair_docs=defaultdict(set);pair_hosts=defaultdict(set)
    for url,d in docs.items():
        terms=sorted(d["terms"]&valid)
        for i,a in enumerate(terms):
            for b in terms[i+1:]:
                pair_docs[(a,b)].add(url);pair_hosts[(a,b)].add(d["host"])
    edges=[]
    for (a,b),urls in pair_docs.items():
        hosts=pair_hosts[(a,b)]
        if len(hosts)<min_publishers or len(urls)<2:continue
        # Lift against generic high-frequency terms, but do not call it significance.
        lift=len(urls)*len(docs)/max(1,len(term_docs[a])*len(term_docs[b]))
        evidence=sorted(urls,key=lambda u:(docs[u]["host"],u))
        # One illustrative URL per host, capped; preserve all evidence counts.
        examples=[];seen=set()
        for url in evidence:
            d=docs[url]
            if d["host"] in seen:continue
            seen.add(d["host"])
            examples.append({"url":url,"publisher_host":d["host"],"publisher_title":d["title"]})
            if len(examples)>=8:break
        edges.append({"terms":[a,b],"co_mention_documents":len(urls),
                      "publisher_hosts_observed":len(hosts),"lift_descriptive":round(lift,3),
                      "supporting_documents":examples,
                      "status":"unverified_co_mention_not_epistemic_relation",
                      "relation_type":"undetermined"})
    edges.sort(key=lambda e:(-e["publisher_hosts_observed"],-e["lift_descriptive"],
                             -e["co_mention_documents"],e["terms"]))
    return {"schema_version":1,"purpose":"blind_relation_hypotheses",
            "query_seed_terms":[],"documents_examined":len(docs),
            "edges":edges[:max_edges],"automatic_topic_creation":False,
            "limitations":["Shared title terms cannot establish causal, contradictory or corroborating relationships.",
                           "No article bodies or claims were examined.",
                           "Publisher host diversity is not independent reporting.",
                           "Named entities and multilingual paraphrases can be missed.",
                           "Term-pair edges are candidates for document-level epistemic review, not facts."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("snapshot",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=discover(json.loads(a.snapshot.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"documents":result["documents_examined"],"relation_candidates":len(result["edges"]),
                      "top_edges":[{"terms":x["terms"],"publisher_hosts":x["publisher_hosts_observed"],
                                    "evidence":x["supporting_documents"][:2]} for x in result["edges"][:8]]},
                     ensure_ascii=False))
if __name__=="__main__":main()
