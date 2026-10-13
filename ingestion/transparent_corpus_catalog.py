"""Transparent editorial inventory of a frozen RSS corpus.

Never confuses feed descriptions with article bodies, independent corroboration,
verified claims, or approved syndication rights.
"""
import argparse,collections,hashlib,json,re
from pathlib import Path
from urllib.parse import urlsplit

def build(snapshot,neighbors=None,*,max_groups=120):
    by_url={}
    for row in snapshot.get("items",[]):
        url=row.get("url")
        if not isinstance(url,str) or urlsplit(url).scheme!="https":continue
        if url not in by_url:by_url[url]=dict(row)
        elif len(row.get("description") or "")>len(by_url[url].get("description") or ""):
            by_url[url]=dict(row)
    docs={}
    for url,row in by_url.items():
        description=" ".join((row.get("description") or "").split())
        tier="rss_extended_description" if len(description)>=160 else ("rss_short_description" if len(description)>=60 else "metadata_only")
        docs[url]={"url":url,"title":row.get("title"),"publisher":row.get("publisher"),
          "source_id":row.get("source_id"),"published_raw":row.get("published_raw"),
          "authors":row.get("authors") or [],"content_tier":tier,
          "description":description[:1200],"description_sha256":hashlib.sha256(description.encode()).hexdigest() if description else None,
          "body_access_tested":False,"body_acquired":False,"access_status":"not_tested",
          "rights_for_republication":"not_confirmed","claim_verification":"not_performed",
          "classification":"unassigned_content_review_required"}
    neighbors=(neighbors or {}).get("pairs",[])
    groups=[];grouped=set();candidates=0
    for pair in sorted(neighbors,key=lambda x:-x.get("similarity",0)):
        a=pair.get("left",{}).get("url");b=pair.get("right",{}).get("url")
        if a not in docs or b not in docs or a in grouped or b in grouped:continue
        if docs[a]["content_tier"]=="metadata_only" or docs[b]["content_tier"]=="metadata_only":continue
        candidates+=1
        if len(groups)>=max_groups:continue
        grouped.update((a,b))
        groups.append({"id":"candidate-"+str(len(groups)+1),"presentation":"multi_source_candidate_not_synthesis",
          "source_urls":[a,b],"similarity":pair.get("similarity"),
          "same_event_verified":False,"claims_compared":False,"independent_origins_verified":False,
          "reason":"semantic neighbor with source-attributed RSS descriptions; editorial review needed"})
    singles=[]
    for url,doc in docs.items():
        if url in grouped:continue
        singles.append({"url":url,"presentation":"original_source_with_rss_description" if doc["content_tier"]!="metadata_only" else "original_source_metadata_only",
                        "synthesis_generated":False,"reason":"no verified multi-source claim alignment"})
    tiers=dict(collections.Counter(x["content_tier"] for x in docs.values()))
    return {"schema_version":1,"purpose":"transparent_large_corpus_editorial_inventory",
      "coverage":{"rss_observations":len(snapshot.get("items",[])),"distinct_documents":len(docs),
        "content_tiers":tiers,"semantic_neighbor_pairs_input":len(neighbors),
        "candidate_multisource_groups":len(groups),"documents_in_candidate_groups":len(grouped),
        "single_original_sources":len(singles),"body_access_tested":0,"full_bodies_acquired":0,
        "verified_claim_relations":0,"approved_multisource_syntheses":0},
      "documents":list(docs.values()),"multi_source_candidates":groups,
      "single_sources":singles,"limitations":[
       "The frozen RSS snapshot has no evidence of per-article body access attempts.",
       "RSS descriptions do not establish full-text availability or permission to republish.",
       "Semantic pairs are candidate associations, never verified event identity.",
       "The catalog is a research preview; publication requires rights and editorial review."],
      "publication_approved":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("snapshot",type=Path)
    p.add_argument("--neighbors",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=build(json.loads(a.snapshot.read_text(encoding="utf-8")),
      json.loads(a.neighbors.read_text(encoding="utf-8")) if a.neighbors else None)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r["coverage"],ensure_ascii=False))
if __name__=="__main__":main()
