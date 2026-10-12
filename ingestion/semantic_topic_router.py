"""Review-only multilingual embedding routing into a CLOSED existing-topic catalog.

No topic, hashtag section or community is created. Model inference is opt-in,
never replaced silently by lexical matching. Scores are not calibrated probabilities.
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

MODEL="intfloat/multilingual-e5-small"

def existing_topics(catalog):
    topics=catalog.get("topics",[])
    if not isinstance(topics,list) or len(topics)>200:
        raise ValueError("Invalid existing topic catalog")
    result=[]
    seen=set()
    for t in topics:
        if not isinstance(t,dict) or not isinstance(t.get("id"),str) or not t.get("title"):
            continue
        if t["id"] in seen:continue
        seen.add(t["id"])
        context="; ".join(str(x) for x in [t["title"],t.get("description",""),
                       *(t.get("questions") or [])][:15])[:1600]
        result.append({"id":t["id"],"title":t["title"],"context":context})
    return result

def _cos(a,b):
    if len(a)!=len(b) or not a:return 0.0
    den=math.sqrt(sum(x*x for x in a))*math.sqrt(sum(y*y for y in b))
    return sum(x*y for x,y in zip(a,b))/den if den else 0.0

def route(observations,topics,embed,*,min_accounts=2,min_posts=2,
          threshold=0.84,margin=0.06,max_groups=150):
    if not 0<=threshold<=1 or not 0<=margin<=1 or not 1<=max_groups<=500:
        raise ValueError("Invalid routing thresholds")
    groups=defaultdict(lambda:{"posts":set(),"accounts":set(),"contexts":[],"urls":set()})
    for post in observations:
        meta=post.get("metadata") or {}
        tags=meta.get("hashtags") or []
        if not isinstance(tags,list):continue
        for raw in set(x.casefold().lstrip("#") for x in tags if isinstance(x,str)):
            if not 3<=len(raw)<=64:continue
            g=groups[raw]
            if post.get("url"):g["posts"].add(post["url"])
            if post.get("source_id"):g["accounts"].add(post["source_id"])
            text=(meta.get("text_preview") or post.get("title") or "")[:700]
            if text and text not in g["contexts"]:g["contexts"].append(text)
            for url in meta.get("linked_documents") or []:
                if isinstance(url,str) and url.startswith("https://"):g["urls"].add(url)
    eligible=[(tag,g) for tag,g in sorted(groups.items())
              if len(g["posts"])>=min_posts and len(g["accounts"])>=min_accounts
              and g["contexts"]][:max_groups]
    # E5 uses query prefixes for symmetric semantic similarity.
    texts=["query: "+t["context"] for t in topics]+[
        "query: #"+tag+"; "+"; ".join(g["contexts"][:8])[:1800] for tag,g in eligible]
    vectors=embed(texts) if texts else []
    if len(vectors)!=len(texts):raise ValueError("Embedding backend returned wrong count")
    n=len(topics)
    proposals=[];abstained=[]
    for idx,(tag,g) in enumerate(eligible):
        ranked=sorted(((_cos(vectors[n+idx],vectors[i]),topics[i])
                       for i in range(n)),key=lambda x:-x[0])
        top=ranked[0] if ranked else None
        runner=ranked[1][0] if len(ranked)>1 else 0
        if not top or top[0]<threshold or (len(ranked)>1 and top[0]-runner<margin):
            abstained.append({"hashtag":tag,"best_topic_id":top[1]["id"] if top else None,
                              "best_score":round(top[0],4) if top else None,
                              "reason":"below_threshold_or_ambiguous"})
            continue
        proposals.append({"hashtag":tag,"topic_id":top[1]["id"],
                          "topic_title":top[1]["title"],"cosine_similarity":round(top[0],4),
                          "runner_up_similarity":round(runner,4),
                          "supporting_posts":sorted(g["posts"])[:12],
                          "linked_document_hints":sorted(g["urls"])[:12],
                          "observed_accounts_unverified":len(g["accounts"]),
                          "status":"review_only_not_published"})
    return {"schema_version":1,"model":MODEL,"purpose":"closed_catalog_semantic_routing",
            "topics_considered":n,"hashtags_observed":len(groups),
            "eligible_groups":len(eligible),"proposals":proposals,"abstentions":abstained,
            "created_topics":[],"created_hashtag_sections":[],
            "automatic_publication":False,
            "limitations":["Similarity is not a calibrated probability or factual verification.",
                           "High similarity may reflect co-occurrence rather than topical relevance.",
                           "All proposals require review; no topic is created.",
                           "Account independence and link authenticity are unverified."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--social",type=Path,required=True)
    p.add_argument("--catalog",type=Path,default=Path("data/catalog.json"))
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--model",default=MODEL)
    p.add_argument("--threshold",type=float,default=0.84)
    p.add_argument("--margin",type=float,default=0.06)
    p.add_argument("--live-model",action="store_true")
    a=p.parse_args()
    if not a.live_model:
        print(json.dumps({"dry_run":True,"model":a.model,"download_or_inference":False}))
        return
    if a.model!=MODEL:raise ValueError("Model change requires explicit code review")
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit("Install optional sentence-transformers dependency explicitly") from exc
    payload=json.loads(a.social.read_text(encoding="utf-8"))
    if not isinstance(payload.get("observations"),list):
        raise ValueError("Raw social observations required")
    topics=existing_topics(json.loads(a.catalog.read_text(encoding="utf-8")))
    model=SentenceTransformer(a.model)
    def embed(texts):
        return model.encode(texts,normalize_embeddings=True,batch_size=16).tolist()
    result=route(payload["observations"],topics,embed,threshold=a.threshold,margin=a.margin)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"eligible":result["eligible_groups"],"proposals":len(result["proposals"]),
                      "abstentions":len(result["abstentions"]),"created_topics":0}))
if __name__=="__main__":main()
