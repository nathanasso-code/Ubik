"""Conservative progressive nucleus expansion over existing candidate-pair edges.

This is candidate discovery, never automatic event merging. A candidate must
have direct evidence links to at least two independent nucleus members.
No transitive-only chaining; no LLM calls or article bodies persisted.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

def expand(pairs, seeds, min_support=2, limit=20):
    edges=defaultdict(dict)
    meta={}
    for pair in pairs:
        a,b=pair["left"],pair["right"]
        ua,ub=a["url"],b["url"]
        if ua==ub:continue
        score=float(pair.get("score",0))
        if score<=0:continue
        meta[ua]=a;meta[ub]=b
        edges[ua][ub]=max(score,edges[ua].get(ub,0))
        edges[ub][ua]=max(score,edges[ub].get(ua,0))
    nucleus=set(seeds)
    if len(nucleus)<2:raise ValueError("At least two independently verified seed sources required")
    results=[]
    # Fixed seeds: never promote unreviewed candidates to verified members.
    for url,neighbors in edges.items():
        if url in nucleus:continue
        matched=[s for s in nucleus if s in neighbors]
        hosts={meta[s].get("publisher") or s.split("/")[2] for s in matched}
        if len(matched)<min_support or len(hosts)<min_support:continue
        scores=[neighbors[s] for s in matched]
        results.append({"url":url,"title":meta[url].get("title",""),
                        "supporting_seed_urls":matched,
                        "support_count":len(matched),
                        "mean_similarity":round(sum(scores)/len(scores),4),
                        "status":"candidate_requires_event_identity_review"})
    results.sort(key=lambda x:(-x["support_count"],-x["mean_similarity"],x["url"]))
    return {"schema_version":1,"method":"multi_anchor_nucleus_expansion",
            "verified_seed_urls":sorted(nucleus),"candidate_count":len(results),
            "candidates":results[:limit],
            "limitations":["Seed pairs must be independently verified as the same event.",
                           "Only edges present in the supplied candidate graph are discoverable.",
                           "No automatic merge; review original texts and event identity first.",
                           "A top-100 pair graph severely limits recall; full edge retrieval is needed."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("pairs",type=Path)
    p.add_argument("--seed",action="append",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    data=json.loads(args.pairs.read_text())
    result=expand(data["top_pairs"],args.seed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Nucleus expansion:",json.dumps({"candidates":result["candidate_count"]}))
if __name__=="__main__":main()
