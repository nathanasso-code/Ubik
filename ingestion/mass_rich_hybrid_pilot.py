"""Acquire a substantial, explicitly licensed Europe PMC corpus and prepare rich-text LLM candidates."""
import argparse, hashlib, json, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from ingestion.europe_pmc_licensed_texts import acquire
from ingestion.rich_text_corpus import build
from ingestion.llm_semantic_adapter import run as llm_run

BASE="https://www.ebi.ac.uk/europepmc/webservices/rest/"
TOPICS=["OPEN_ACCESS:Y AND climate","OPEN_ACCESS:Y AND artificial intelligence","OPEN_ACCESS:Y AND public health"]
def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"UbikResearchBot/0.1 (ubik.research@gmail.com)"})
    with urllib.request.urlopen(req,timeout=25) as response:return json.load(response)
def discover(per_topic=70,get=get_json):
    docs=[];seen=set();errors=[]
    for topic in TOPICS:
        url=BASE+"search?"+urllib.parse.urlencode({"query":topic,"format":"json","pageSize":min(per_topic,100)})
        try: results=get(url).get("resultList",{}).get("result",[])
        except (OSError,ValueError,TimeoutError) as exc:
            errors.append({"topic":topic,"error":type(exc).__name__,"http_status":getattr(exc,"code",None)});continue
        for x in results:
            pmcid=x.get("pmcid")
            if not pmcid or pmcid in seen:continue
            seen.add(pmcid)
            docs.append({"url":"https://europepmc.org/articles/"+pmcid,"source_id":"europepmc",
                         "title":x.get("title",""),"description":re.sub("<[^>]+>"," ",x.get("abstractText") or "")[:5000],
                         "pmcid":pmcid,"topic_seed":topic})
    return {"items":docs,"errors":errors}
def shortlist(documents,budget=50):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    if len(documents)<2:return {"queue":[],"coverage":{"documents":len(documents),"pairs":0}}
    snippets=[(d["title"]+" "+d["text"][:16000]) for d in documents]
    matrix=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=50000,sublinear_tf=True).fit_transform(snippets)
    sims=cosine_similarity(matrix)
    pairs=[]
    for i in range(len(documents)):
        for j in range(i+1,len(documents)):
            score=float(sims[i,j])
            if score<0.08:continue
            a,b=documents[i],documents[j]
            pairs.append({"pair_id":hashlib.sha256((a["url"]+"|"+b["url"]).encode()).hexdigest()[:16],
                          "url_a":a["url"],"url_b":b["url"],"similarity":round(score,4),
                          "title_a":a["title"],"title_b":b["title"],"status":"unverified"})
    pairs.sort(key=lambda p:-p["similarity"])
    # Prevent one prolific document from consuming the entire review budget.
    selected=[];counts={}
    for p in pairs:
        if counts.get(p["url_a"],0)>=4 or counts.get(p["url_b"],0)>=4:continue
        selected.append(p)
        for key in ("url_a","url_b"):counts[p[key]]=counts.get(p[key],0)+1
        if len(selected)>=budget:break
    return {"queue":selected,"coverage":{"documents":len(documents),"candidate_pairs":len(pairs),"pairs":len(selected)},
            "limitations":["Lexical retrieval is not proof of same event, same claim or contradiction."]}
def experiment(discovered,rich,budget=30,llm_limit=10,execute=False,endpoint="",model="",key=""):
    docs=rich["documents"];queue=shortlist(docs,budget)
    llm=llm_run(queue,docs,limit=llm_limit,execute=execute,endpoint=endpoint,model=model,key=key)
    return {"schema_version":1,"discovery":{"candidates":len(discovered["items"]),"errors":discovered["errors"]},
            "rich_coverage":rich["coverage"],"retrieval":queue,"llm":llm,
            "limitations":["Only licensed substantial bodies enter candidate selection.",
              "Without an endpoint/key the LLM stage is a dry-run, not semantic inference.",
              "All relation outputs are review-only; no automatic article merging."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True);p.add_argument("--texts",type=Path,required=True)
    p.add_argument("--per-topic",type=int,default=70);p.add_argument("--max-acquire",type=int,default=160)
    p.add_argument("--budget",type=int,default=30);p.add_argument("--llm-limit",type=int,default=10)
    p.add_argument("--execute",action="store_true");a=p.parse_args()
    import os
    discovered=discover(a.per_topic)
    acquired=acquire(discovered,a.texts,max_items=a.max_acquire)
    rich=build(a.texts,minimum_chars=800)
    result=experiment(discovered,rich,a.budget,a.llm_limit,a.execute,os.getenv("UBIK_LLM_ENDPOINT",""),
                      os.getenv("UBIK_LLM_MODEL",""),os.getenv("UBIK_LLM_API_KEY",""))
    result["acquisition"]=acquired["coverage"]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"discovery":result["discovery"],"acquisition":result["acquisition"],
      "rich_coverage":result["rich_coverage"],"retrieval":result["retrieval"]["coverage"],
      "llm":result["llm"]["coverage"]}))
if __name__=="__main__":main()
