"""Auditable hybrid discovery: join social-shared URLs with publisher documents.

Social posts are discovery signals, not editorial confirmations. Accepts existing
topic-social run exports without requiring a fresh topic-seeded search.
"""
import argparse,json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from .contracts import canonical_url_hint

def hybrid_links(rss_snapshot,social_runs,*,max_documents=3000):
    if not 1<=max_documents<=20000:raise ValueError("Invalid document budget")
    documents={}
    for item in rss_snapshot.get("items",[]):
        url=item.get("url")
        if not isinstance(url,str):continue
        try:key=canonical_url_hint(url)
        except (ValueError,TypeError):continue
        documents.setdefault(key,{"url":key,"publisher_titles":[],"rss_sources":set(),
                                  "social_post_urls":set(),"social_providers":set(),
                                  "social_accounts":set(),"discovery_origins":set()})
        d=documents[key];d["publisher_titles"].append(item.get("title",""))
        d["rss_sources"].add(item.get("source_id",""))
        d["discovery_origins"].add("publisher_rss")
    social_observations=0
    for run in social_runs:
        # Existing topic-social output is a ranked document index with post URLs.
        for item in run.get("documents",[]):
            url=item.get("url")
            if not isinstance(url,str):continue
            try:key=canonical_url_hint(url)
            except (ValueError,TypeError):continue
            if urlsplit(key).scheme not in ("http","https"):continue
            d=documents.setdefault(key,{"url":key,"publisher_titles":[],"rss_sources":set(),
                                        "social_post_urls":set(),"social_providers":set(),
                                        "social_accounts":set(),"discovery_origins":set()})
            d["social_post_urls"].update(item.get("post_urls") or [])
            d["social_providers"].update(item.get("providers") or [])
            d["discovery_origins"].add("social_shared_url")
            social_observations+=1
    result=[]
    for d in documents.values():
        if len(result)>=max_documents:break
        result.append({"url":d["url"],"publisher_titles":list(dict.fromkeys(t for t in d["publisher_titles"] if t)),
                       "rss_sources":sorted(d["rss_sources"]- {""}),
                       "social_post_urls":sorted(d["social_post_urls"])[:30],
                       "social_providers":sorted(d["social_providers"]),
                       "discovery_origins":sorted(d["discovery_origins"]),
                       "status":"unverified_document_hint"})
    return {"schema_version":1,"purpose":"hybrid_document_discovery",
            "documents":result,"rss_document_hints":sum("publisher_rss" in d["discovery_origins"] for d in result),
            "social_document_hints":sum("social_shared_url" in d["discovery_origins"] for d in result),
            "cross_channel_document_hints":sum(len(d["discovery_origins"])==2 for d in result),
            "social_url_observations":social_observations,
            "limitations":["Social URLs without publisher metadata are not articles verified as readable.",
                           "Cross-channel overlap is not independent factual corroboration.",
                           "Inputs may have been gathered with topic queries; not a global social firehose.",
                           "The output does not assign topics or merge events."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--rss",required=True,type=Path)
    p.add_argument("--social",action="append",type=Path,default=[])
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=hybrid_links(json.loads(a.rss.read_text(encoding="utf-8")),
                        [json.loads(x.read_text(encoding="utf-8")) for x in a.social])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("documents","limitations")}))
if __name__=="__main__":main()
