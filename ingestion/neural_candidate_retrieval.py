"""Neural retrieval supplement on a FROZEN metadata-first corpus.

Keep every original TF-IDF edge; add top-k cosine candidates from multilingual
sentence embeddings, especially for isolated sources. Never infer event identity
or publish cards from vector similarity. Deterministic ordering and diagnostics.
"""
import argparse,collections,json,math
from pathlib import Path

MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def augment(data,model_name=MODEL,top_k=4,threshold=.67,max_day_gap=7,batch_size=32):
    from sentence_transformers import SentenceTransformer
    from ingestion.metadata_first_candidates import published
    docs=data["sources"]
    texts=[(d.get("title") or "")+". "+(d.get("description") or "")[:650] for d in docs]
    model=SentenceTransformer(model_name)
    vectors=model.encode(texts,batch_size=batch_size,normalize_embeddings=True,show_progress_bar=False)
    # Bounded 979-document pilot: cosine matrix is small enough for NumPy.
    import numpy as np
    matrix=np.asarray(vectors,dtype=np.float32) @ np.asarray(vectors,dtype=np.float32).T
    existing={tuple(sorted((e["a"],e["b"]))) for e in data["candidate_pairs"]}
    previously_linked={x for pair in existing for x in pair}
    proposed={}
    for i,d in enumerate(docs):
        sims=matrix[i]
        order=np.argsort(-sims,kind="stable")
        chosen=0
        for j in order:
            j=int(j)
            if j==i:continue
            a=published(d);b=published(docs[j])
            if a and b and abs((a-b).days)>max_day_gap:continue
            score=float(sims[j])
            if score<threshold:break
            pair=tuple(sorted((d["id"],docs[j]["id"])))
            if pair not in existing:
                proposed[pair]=max(proposed.get(pair,0),round(score,5))
            chosen+=1
            if chosen>=top_k:break
    additions=[{"a":a,"b":b,"score":score,"method":"multilingual_embedding","status":"candidate_only_not_event_identity"}
               for (a,b),score in sorted(proposed.items())]
    edges=data["candidate_pairs"]+additions
    graph=collections.defaultdict(set)
    for e in edges:graph[e["a"]].add(e["b"]);graph[e["b"]].add(e["a"])
    seen=set();contexts=[]
    for sid in sorted(graph):
        if sid in seen:continue
        stack=[sid];seen.add(sid);members=[]
        while stack:
            k=stack.pop();members.append(k)
            for other in graph[k]:
                if other not in seen:seen.add(other);stack.append(other)
        contexts.append({"source_ids":sorted(members),"status":"requires_semantic_event_review"})
    newly_linked={x for e in additions for x in (e["a"],e["b"])}
    result={**data,"method":"metadata_tfidf_plus_multilingual_embeddings",
      "candidate_pairs":edges,"review_contexts":contexts,
      "summary":{**data["summary"],"candidate_pairs":len(edges),"review_contexts":len(contexts),
        "sources_with_candidates":len(graph),"standalone_sources":len(docs)-len(graph),
        "embedding_new_edges":len(additions),"previously_isolated_sources_retrieved":len(newly_linked-previously_linked),
        "largest_review_context":max((len(x["source_ids"]) for x in contexts),default=0)},
      "retrieval_audit":{"model":model_name,"top_k":top_k,"threshold":threshold,
        "baseline_edges":len(data["candidate_pairs"]),"new_embedding_edges":len(additions),
        "baseline_isolated_sources":len(docs)-len(previously_linked),
        "newly_retrieved_isolated_sources":len(newly_linked-previously_linked),
        "note":"Counts measure candidates, NOT true same-event recall."}}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--top-k",type=int,default=4)
    p.add_argument("--threshold",type=float,default=.67)
    a=p.parse_args()
    data=json.loads(a.input.read_text())
    out=augment(data,top_k=a.top_k,threshold=a.threshold)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("NEURAL_RETRIEVAL",json.dumps(out["summary"],ensure_ascii=False))
if __name__=="__main__":main()
