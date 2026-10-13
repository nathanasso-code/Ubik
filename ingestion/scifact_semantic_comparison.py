"""Compare lexical and multilingual embedding evidence ranking on SciFact dev.

Same annotated claim-document-rationale pairs; oracle document IDs.
No inference about factual entailment or open retrieval.
"""
import argparse,json
from pathlib import Path
from ingestion.scifact_gold_baseline import URL,gold_rows,tokens
import urllib.request
def examples(rows,corpus):
 for row in rows:
  for doc_id,evs in row.get("evidence",{}).items():
   sentences=corpus.get(str(doc_id),[])
   for ev in evs:
    gold=set(ev.get("sentences",[]))
    if sentences and gold:
     yield row.get("claim",""),sentences,gold
def evaluate(rows,corpus,model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
 from sentence_transformers import SentenceTransformer
 import numpy as np
 model=SentenceTransformer(model_name)
 samples=list(examples(rows,corpus))
 unique=list(dict.fromkeys([s for claim,sentences,gold in samples for s in [claim,*sentences]]))
 vectors=model.encode(unique,batch_size=64,normalize_embeddings=True,show_progress_bar=False)
 lookup={text:vec for text,vec in zip(unique,vectors)}
 stats={"lexical":{"hit1":0,"hit3":0},"semantic":{"hit1":0,"hit3":0}}
 for claim,sentences,gold in samples:
  ct=tokens(claim)
  lexical=sorted(range(len(sentences)),key=lambda i:len(ct&tokens(sentences[i]))/max(1,len(ct|tokens(sentences[i]))),reverse=True)
  semantic=sorted(range(len(sentences)),key=lambda i:float(np.dot(lookup[claim],lookup[sentences[i]])),reverse=True)
  for label,ranked in (("lexical",lexical),("semantic",semantic)):
   stats[label]["hit1"]+=bool(set(ranked[:1])&gold)
   stats[label]["hit3"]+=bool(set(ranked[:3])&gold)
 n=len(samples)
 return {"schema_version":1,"dataset":"SciFact dev","model":model_name,
  "evaluation":{"gold_rationales_with_abstract":n,
   **{k:{"hit_at_1":v["hit1"],"hit_at_3":v["hit3"],
    "recall_at_1":round(v["hit1"]/n,4) if n else None,
    "recall_at_3":round(v["hit3"]/n,4) if n else None} for k,v in stats.items()}},
  "limitations":["Oracle gold document ID; this is evidence sentence retrieval, not claim verification.",
   "Multiple rationales per claim-document may be counted separately.",
   "No test split, significance interval or cross-domain validation yet."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
 p.add_argument("--archive",type=Path);a=p.parse_args()
 blob=a.archive.read_bytes() if a.archive else urllib.request.urlopen(URL,timeout=60).read(30_000_001)
 if len(blob)>30_000_000:raise ValueError("Dataset size limit")
 rows,corpus=gold_rows(blob);result=evaluate(rows,corpus)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result["evaluation"]))
if __name__=="__main__":main()
