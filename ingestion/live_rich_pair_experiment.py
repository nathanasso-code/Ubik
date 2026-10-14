"""Paired title-vs-body experiment on live publicly readable news.

Bodies remain in memory. Reports contain only metrics and URLs, not copyrighted text.
"""
import argparse,json,re,collections,math
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import fetch_one,USER_AGENT
from ingestion.live_get_text_probe import Extractor

STOP=set("the and for with from this that have into after over about said says will were their a an of to in on at as by is are was be it its new not".split())
def words(s):
    return [x for x in re.findall(r"[a-z]{3,}",s.lower()) if x not in STOP]
def cosine(a,b):
    x,y=collections.Counter(words(a)),collections.Counter(words(b))
    if not x or not y:return 0.
    return sum(v*y.get(k,0) for k,v in x.items())/math.sqrt(sum(v*v for v in x.values())*sum(v*v for v in y.values()))
def chunks(text,size=130,step=85):
    w=text.split()
    return [" ".join(w[i:i+size]) for i in range(0,len(w),step) if len(w[i:i+size])>=40][:50]
def analyze(snapshot,hybrid,limit=24,fetch=fetch_one):
    byurl={d["url"]:d for d in snapshot.get("items",[]) if d.get("url")}
    pairs=hybrid.get("pairs",[])[:limit]
    urls=list(dict.fromkeys(u for p in pairs for u in (p["url_a"],p["url_b"])))
    texts={};failures=collections.Counter()
    for url in urls:
        p=urlsplit(url);host=p.hostname
        if p.scheme!="https" or not host:
            failures["invalid_url"]+=1;continue
        try:
            robots=fetch("https://"+host+"/robots.txt",{host},timeout=6)
            rp=RobotFileParser();rp.parse(robots.splitlines())
            if not rp.can_fetch(USER_AGENT,url):
                failures["robots_disallowed"]+=1;continue
            html=fetch(url,{host},timeout=9)
            ext=Extractor();ext.feed(html)
            article=" ".join("".join(ext.article).split())
            visible=" ".join("".join(ext.text).split())
            body=article if len(article)>=1200 else visible
            if len(body)<2000:
                failures["insufficient_body"]+=1;continue
            texts[url]=body[:40000]
        except (OSError,ValueError,TimeoutError,PermissionError):
            failures["fetch_failed"]+=1
    rows=[]
    for pair in pairs:
        a,b=byurl.get(pair["url_a"]),byurl.get(pair["url_b"])
        if not a or not b:continue
        ta,tb=texts.get(pair["url_a"]),texts.get(pair["url_b"])
        if not ta or not tb:continue
        title=cosine(a.get("title",""),b.get("title",""))
        desc=cosine(a.get("title","")+" "+(a.get("description") or ""),b.get("title","")+" "+(b.get("description") or ""))
        ca,cb=chunks(ta),chunks(tb)
        ranked=sorted((cosine(x,y) for x in ca for y in cb),reverse=True)
        rows.append({"url_a":pair["url_a"],"url_b":pair["url_b"],
            "title_similarity":round(title,4),"title_description_similarity":round(desc,4),
            "best_chunk_similarity":round(ranked[0],4) if ranked else None,
            "mean_top_3_chunk_similarity":round(sum(ranked[:3])/min(3,len(ranked)),4) if ranked else None,
            "body_characters_a":len(ta),"body_characters_b":len(tb),
            "relation_label":"unverified","source_text_retained":False})
    return {"schema_version":1,"coverage":{"candidate_pairs":len(pairs),
        "unique_urls_requested":len(urls),"substantial_bodies_read_in_memory":len(texts),
        "pairs_with_two_substantial_bodies":len(rows),"failures":dict(failures)},
        "pairs":rows,"limitations":["No article bodies stored or reproduced.",
        "Chunk lexical similarity is a diagnostic, not semantic entailment or event identity.",
        "Candidate-pair selection is biased toward metadata similarity.",
        "No human gold labels; accuracy cannot be inferred."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("--snapshot",type=Path,required=True)
    p.add_argument("--hybrid",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int,default=24);a=p.parse_args()
    out=analyze(json.loads(a.snapshot.read_text()),json.loads(a.hybrid.read_text()),a.limit)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(out["coverage"]))
if __name__=="__main__":main()
