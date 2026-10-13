"""Reproducible title-level empirical audit, separate from full-body claim verification."""
import argparse,json,random
from pathlib import Path

def audit(report,*,seed=20261013,sample_size=30):
    pairs=report.get("pairs",[])
    rng=random.Random(seed)
    chosen=sorted(rng.sample(range(len(pairs)),min(sample_size,len(pairs))))
    items=[]
    for i in chosen:
        p=pairs[i];left=p.get("left") or {};right=p.get("right") or {}
        items.append({"frozen_rank":i+1,"similarity":p.get("similarity"),
                      "left":{"url":left.get("url"),"title":left.get("title")},
                      "right":{"url":right.get("url"),"title":right.get("title")},
                      "label":"not_reviewed",
                      "questions":["Same event and matching time window?",
                                   "Distinct events sharing keywords?",
                                   "Potentially evolving count rather than contradictory claims?",
                                   "Are publishers relying on the same original source?"]})
    return {"schema_version":1,"sampling_frame":"retrieved_semantic_pairs_only",
            "frozen_pair_count":len(pairs),"seed":seed,"sample_size":len(items),
            "items":items,"precision_estimate":None,"recall_estimate":None,
            "limitations":["Unlabeled random samples do not measure precision.",
                           "Retrieval-only samples cannot estimate recall over all document pairs.",
                           "No full publisher bodies or factual claims were verified."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("report",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--seed",type=int,default=20261013)
    p.add_argument("--sample-size",type=int,default=30)
    a=p.parse_args()
    result=audit(json.loads(a.report.read_text(encoding="utf-8")),seed=a.seed,sample_size=a.sample_size)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"random_review_sample":result["sample_size"],"precision_estimate":None}))
if __name__=="__main__":main()
