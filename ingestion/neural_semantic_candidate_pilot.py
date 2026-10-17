"""Neural multilingual embedding retrieval compared with a frozen TF-IDF baseline.

Candidates are unverified; model scores are not probabilities of same-event.
"""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit

def retrieve(rows,baseline,model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",top_k=100):
    from sentence_transformers import SentenceTransformer
    import numpy as np
    docs=list({r["url"]:r for r in rows if r.get("url") and r.get("title")}.values())
    texts=[str(d["title"])+" . "+str(d.get("description") or "")[:500] for d in docs]
    model=SentenceTransformer(model_name)
    vectors=model.encode(texts,batch_size=32,normalize_embeddings=True,show_progress_bar=False)
    baseline_keys={tuple(sorted((p["left"]["url"],p["right"]["url"]))) for p in baseline["top_pairs"]}
    scored=[]
    # Blockwise matrix multiplication avoids allocating all-pairs scores for larger corpora.
    for i in range(0,len(docs),128):
        scores=np.asarray(vectors[i:i+128])@np.asarray(vectors).T
        for local,row in enumerate(scores):
            a=i+local
            for b in range(a+1,len(docs)):
                if urlsplit(docs[a]["url"]).hostname==urlsplit(docs[b]["url"]).hostname:continue
                key=tuple(sorted((docs[a]["url"],docs[b]["url"])))
                if key in baseline_keys:continue
                scored.append((float(row[b]),a,b))
    scored.sort(reverse=True)
    result=[]
    for score,a,b in scored[:top_k]:
        result.append({"similarity":round(score,4),"left":{"url":docs[a]["url"],"title":docs[a]["title"],"publisher":docs[a].get("publisher")},
                       "right":{"url":docs[b]["url"],"title":docs[b]["title"],"publisher":docs[b].get("publisher")},
                       "status":"unverified_requires_event_identity_review"})
    return {"schema_version":1,"method":"multilingual_neural_sentence_embeddings",
            "model":model_name,"corpus_documents":len(docs),"baseline_pairs":len(baseline_keys),
            "novel_candidate_pairs":len(result),"candidates":result,
            "limitations":["Novel means not in bounded TF-IDF top-k, not proof of same-event.",
                           "Similarity is not calibrated event identity.","Titles and RSS descriptions only; full-text evaluation remains necessary."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path);p.add_argument("baseline",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--top-k",type=int,default=100)
    a=p.parse_args()
    data=retrieve(json.loads(a.input.read_text())["items"],json.loads(a.baseline.read_text()),top_k=min(1000,max(1,a.top_k)))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print("Neural semantic candidate pilot:",json.dumps({"corpus_documents":data["corpus_documents"],"baseline_pairs":data["baseline_pairs"],"novel_candidate_pairs":data["novel_candidate_pairs"],"model":data["model"]}))
    for c in data["candidates"][:15]:
        print("SEMANTIC NOVEL (UNVERIFIED):",c["similarity"],c["left"]["title"],"<>",c["right"]["title"])
if __name__=="__main__":main()
