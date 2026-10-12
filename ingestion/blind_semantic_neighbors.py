"""Blind multilingual semantic neighborhoods from the same frozen RSS corpus.

The nearest-neighbor graph is *not* an epistemic claim or same-event verdict.
No topic, datacenter seed, or manually chosen controversy is used in retrieval.
"""
import argparse,json,math
from pathlib import Path
from urllib.parse import urlsplit

MODEL="intfloat/multilingual-e5-small"

def neighborhoods(snapshot,embed,*,max_documents=500,k=5,min_similarity=0.72):
    if not 2<=max_documents<=1000 or not 1<=k<=20 or not 0<=min_similarity<=1:
        raise ValueError("Invalid semantic neighborhood budget")
    docs=[];seen=set()
    for row in snapshot.get("items",[]):
        url=row.get("url");title=row.get("title")
        if not isinstance(url,str) or not isinstance(title,str) or not title.strip():continue
        host=urlsplit(url).hostname
        if not host or urlsplit(url).scheme not in ("https","http") or url in seen:continue
        seen.add(url)
        docs.append({"url":url,"host":host,"title":title.strip(),"published_raw":row.get("published") or row.get("published_at") or row.get("pubDate")})
        if len(docs)>=max_documents:break
    vectors=embed(["query: "+d["title"] for d in docs]) if docs else []
    if len(vectors)!=len(docs):raise ValueError("Incorrect embedding count")
    normalized=[]
    for v in vectors:
        mag=math.sqrt(sum(float(x)*float(x) for x in v))
        normalized.append([float(x)/mag for x in v] if mag else [0.0 for x in v])
    # One-sided top-k search, with publisher host exclusion and bounded comparisons.
    edges={}
    for i,a in enumerate(docs):
        ranked=[]
        for j,b in enumerate(docs):
            if i==j or a["host"]==b["host"]:continue
            score=sum(x*y for x,y in zip(normalized[i],normalized[j]))
            if score>=min_similarity:ranked.append((score,j))
        ranked.sort(key=lambda x:(-x[0],docs[x[1]]["url"]))
        for score,j in ranked[:k]:
            key=(min(i,j),max(i,j))
            if key not in edges or score>edges[key]:edges[key]=score
    pairs=[]
    for (i,j),score in edges.items():
        a,b=docs[i],docs[j]
        pairs.append({"similarity":round(score,4),
                      "left":a,"right":b,
                      "status":"unreviewed_semantic_neighbor",
                      "relation_type":"undetermined",
                      "same_event_verified":False,
                      "causal_relation_verified":False,
                      "independent_corroboration_verified":False})
    pairs.sort(key=lambda x:(-x["similarity"],x["left"]["url"],x["right"]["url"]))
    return {"schema_version":1,"purpose":"blind_cross_publisher_semantic_neighbors",
            "model":MODEL,"query_seed_terms":[],"topic_seeds_used":False,
            "documents_examined":len(docs),"min_similarity":min_similarity,"top_k_per_document":k,
            "pairs":pairs,"automatic_topic_creation":False,"automatic_publication":False,
            "limitations":["Title-only similarity is not epistemic support, contradiction, causality or event identity.",
                           "Different publisher hosts do not prove independent reporting.",
                           "No model score has been calibrated against labeled data.",
                           "Candidate ranking must be frozen before inspecting held-out examples."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("snapshot",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--min-similarity",type=float,default=.72)
    p.add_argument("--live-model",action="store_true")
    a=p.parse_args()
    if not a.live_model:
        print(json.dumps({"dry_run":True,"network_calls":0}));return
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer(MODEL)
    def embed(texts):return model.encode(texts,normalize_embeddings=True,batch_size=16).tolist()
    result=neighborhoods(json.loads(a.snapshot.read_text(encoding="utf-8")),embed,
                         min_similarity=a.min_similarity)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"documents":result["documents_examined"],"pairs":len(result["pairs"]),
                      "top_pairs":[{"similarity":x["similarity"],"left":x["left"]["title"],
                                    "right":x["right"]["title"],
                                    "urls":[x["left"]["url"],x["right"]["url"]]}
                                   for x in result["pairs"][:12]]},ensure_ascii=False))
if __name__=="__main__":main()
