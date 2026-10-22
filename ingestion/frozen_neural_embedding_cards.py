"""Neural-embedding baseline: preserves every news item and its verified source evidence."""
import argparse,json
from pathlib import Path
from collections import Counter
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def main():
 p=argparse.ArgumentParser()
 p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
 p.add_argument("--model",default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
 p.add_argument("--threshold",type=float,default=0.79)
 a=p.parse_args()
 data=json.loads(a.input.read_text())
 model=SentenceTransformer(a.model,device="cpu")
 out={"method":"neural_sentence_embeddings_complete_linkage","model":a.model,"threshold":a.threshold,"original_run":39822649930,"contexts":[]}
 for ctx in data["contexts"]:
  items=ctx["news"]; n=len(items)
  result={"context":ctx["context"],"news_count":n,"original_cards":len(ctx["cards"]),"cards":[],"nearest_pairs":[]}
  if not n:out["contexts"].append(result);continue
  # Each original extraction has one-to-one evidence anchored to the source.
  evidence_lookup={}
  for card in ctx["cards"]:
   for e in card.get("evidence",[]):
    evidence_lookup[e["news_id"]]=e
  vectors=model.encode([x["title"]+". "+x["summary"] for x in items],normalize_embeddings=True,show_progress_bar=False)
  sim=cosine_similarity(vectors)
  distance=np.clip(1-sim,0,2);np.fill_diagonal(distance,0)
  labels=AgglomerativeClustering(n_clusters=None,distance_threshold=1-a.threshold,metric="precomputed",linkage="complete").fit_predict(distance) if n>1 else [0]
  groups={}
  for item,label in zip(items,labels):groups.setdefault(int(label),[]).append(item)
  for i,members in enumerate(groups.values()):
   # Never collapse source-specific summaries: attach full objects.
   sources=[]
   for m in members:
    sid=m["source_id"]
    source=data["sources"].get(sid,{})
    verified=evidence_lookup.get(m["id"])
    if verified is None:
     match=next((v for v in source.get("news",[]) if v.get("title")==m["title"] and v.get("summary")==m["summary"]),None)
     verified={"source_id":sid,"news_id":m["id"],"source_summary":m["summary"],"passages":match["evidence"] if match else []}
    sources.append({"news_id":m["id"],"source_id":sid,"source_title":source.get("title"),"title":m["title"],"summary":m["summary"],"evidence":verified.get("passages",[])})
   result["cards"].append({"id":f"emb-{ctx['context']}-{i}","title":members[0]["title"],"news_ids":[m["id"] for m in members],"source_ids":list(dict.fromkeys(m["source_id"] for m in members)),"source_summaries":sources,"min_pair_similarity":round(min(float(sim[items.index(x)][items.index(y)]) for x in members for y in members),4)})
  result["nearest_pairs"]=[{"a":items[i]["id"],"b":items[j]["id"],"similarity":round(float(sim[i,j]),4),"title_a":items[i]["title"],"title_b":items[j]["title"]} for i in range(n) for j in range(i+1,n) if sim[i,j]>=0.7]
  result["nearest_pairs"].sort(key=lambda x:-x["similarity"])
  out["contexts"].append(result)
 out["totals"]={"news":sum(x["news_count"] for x in out["contexts"]),"cards":sum(len(x["cards"]) for x in out["contexts"]),"sources_in_cards":len(set(s for c in out["contexts"] for card in c["cards"] for s in card["source_ids"]))}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out["totals"]))
if __name__=="__main__":main()
