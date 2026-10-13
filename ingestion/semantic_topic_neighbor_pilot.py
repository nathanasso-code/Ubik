"""Exploratory semantic topic hierarchy and document-neighbor proposals.

Similarity ranks related content; it does not establish same-event identity.
"""
import argparse,json,re
from pathlib import Path
from ingestion.semantic_topic_router import MODEL,_cos
TAXONOMY={
 "science":{"medicine":["clinical research","public health","neuroscience"],"space":["astronomy","space missions"],"environment":["climate research","biodiversity"]},
 "technology":{"computing":["artificial intelligence","cybersecurity"],"engineering":["energy technology","transport technology"]},
 "society":{"politics":["elections","public policy","international relations"],"economy":["financial markets","employment"],"culture":["arts","education"]},
 "news":{"justice":["criminal trials","courts and sentencing","crime investigations"],"public safety":["accidents","emergencies"],"world affairs":["armed conflict","diplomacy"]},
 "sports":{"competition":["football","tennis","motorsport"],"business":["sports governance"]},
}
def taxonomy_entries():
 return [(a,b,c) for a,bs in TAXONOMY.items() for b,cs in bs.items() for c in cs]
def extract(snapshot,limit=500):
 items=snapshot.get("items",[])
 out=[];seen=set()
 for x in items:
  url=x.get("url")
  title=x.get("title") or ""
  desc=x.get("description") or x.get("summary") or ""
  if not isinstance(url,str) or not url.startswith("http") or not isinstance(title,str) or not isinstance(desc,str):continue
  if url in seen or len(title)<12:continue
  seen.add(url)
  out.append({"url":url,"source_id":x.get("source_id"),"published_at":x.get("published_at") or x.get("published") or x.get("date"),"title":title[:250],"description":desc[:900]})
  if len(out)>=limit:break
 return out
def analyze(snapshot,embed,limit=500,*,min_score=0.70,min_margin=0.015):
 docs=extract(snapshot,limit)
 cats=taxonomy_entries()
 cat_texts=["passage: "+ " > ".join(c) for c in cats]
 doc_texts=["passage: "+d["title"]+"; "+d["description"] for d in docs]
 vectors=embed(cat_texts+doc_texts)
 if len(vectors)!=len(cat_texts)+len(doc_texts):raise ValueError("Unexpected embedding count")
 n=len(cats);out=[]
 for i,d in enumerate(docs):
  ranked=sorted(((round(_cos(vectors[n+i],vectors[j]),4),cats[j]) for j in range(n)),reverse=True)
  top=ranked[0] if ranked else None
  runner=ranked[1][0] if len(ranked)>1 else 0.0
  confident=bool(top and top[0]>=min_score and top[0]-runner>=min_margin)
  macro_scores={}
  for score,path in ranked:
   macro_scores[path[0]]=max(score,macro_scores.get(path[0],-1))
  macro_ranked=sorted(macro_scores.items(),key=lambda x:-x[1])
  macro=macro_ranked[0] if macro_ranked else None
  macro_margin=macro[1]-macro_ranked[1][1] if len(macro_ranked)>1 else 0
  # Macro level remains a candidate even when the narrow path is ambiguous.
  macro_candidate=macro[0] if macro and macro[1]>=min_score else None
  out.append({**d,"macro_category_candidate":macro_candidate,
   "macro_category_score":round(macro[1],4) if macro else None,
   "macro_category_margin":round(macro_margin,4),
   "macro_category_status":"review_candidate" if macro_candidate else "abstain_low_score",
   "taxonomy_candidates":[{"path":list(path),"similarity":score} for score,path in ranked[:3]],
   "proposed_category":list(top[1]) if confident else None,
   "category_status":"review_candidate" if confident else "abstain_low_similarity_or_margin",
   "category_margin":round(top[0]-runner,4) if top else None})
 pairs=[]
 for i,d in enumerate(docs):
  ranked=sorted(((round(_cos(vectors[n+i],vectors[n+j]),4),j) for j in range(len(docs))
    if j!=i and docs[j].get("source_id")!=d.get("source_id")),reverse=True)[:3]
  for score,j in ranked:
   if i<j:
    pairs.append({"url_a":d["url"],"url_b":docs[j]["url"],"similarity":score,
      "status":"semantic_neighbor_not_same_event"})
 pairs.sort(key=lambda x:-x["similarity"])
 return {"schema_version":1,"model":MODEL,"documents":out,"cross_source_neighbors":pairs[:100],
  "coverage":{"documents":len(out),"taxonomy_paths":len(cats),"neighbor_proposals":len(pairs[:100]),
   "category_abstentions":sum(x["proposed_category"] is None for x in out),
   "macro_abstentions":sum(x["macro_category_candidate"] is None for x in out)},
  "limitations":["Taxonomy is an experimental fixed hierarchy, not a validated ontology.",
   "Similarity scores are uncalibrated and labels require manual review.",
   "Semantic neighbors may discuss different events or repeat syndicated content.",
   "Thresholds are provisional and require a manually labeled benchmark.",
   "No automatic article merge, factual verification, or summary generation."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--snapshot",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True);p.add_argument("--limit",type=int,default=400);a=p.parse_args()
 from sentence_transformers import SentenceTransformer
 model=SentenceTransformer(MODEL)
 data=analyze(json.loads(a.snapshot.read_text()),lambda texts:model.encode(texts,batch_size=32,normalize_embeddings=True).tolist(),a.limit)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(data["coverage"]))
if __name__=="__main__":main()
