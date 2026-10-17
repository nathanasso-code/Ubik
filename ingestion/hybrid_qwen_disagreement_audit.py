"""Audit Qwen metadata decisions against retrieval edges on exactly reviewed cases.

This measures disagreement, not correctness. Never treat Qwen output as gold.
"""
import argparse,collections,json
from pathlib import Path

def audit(graph,reviews):
    edge_map={tuple(sorted((e["a"],e["b"]))):e for e in graph["candidate_pairs"]}
    examined=set();accepted=set();rows=[]
    for review in reviews["reviews"]:
        ids=set(review["source_ids"])
        local={p for p in edge_map if set(p)<=ids}
        groups=[set(c["source_ids"]) for c in review["cards"]]
        merged={p for p in local if any(set(p)<=g for g in groups)}
        examined|=local;accepted|=merged
        rows.append({"sources":len(ids),"candidate_edges":len(local),"qwen_accepted_candidate_edges":len(merged),
                     "qwen_rejected_candidate_edges":len(local-merged),"card_count":len(groups),
                     "invalid_groups":len(review.get("invalid_groups",[]))})
    methods=collections.defaultdict(lambda:{"candidate_edges":0,"qwen_accepted":0,"qwen_rejected":0})
    for pair in examined:
        e=edge_map[pair];method=e.get("method","tfidf")
        methods[method]["candidate_edges"]+=1
        methods[method]["qwen_accepted" if pair in accepted else "qwen_rejected"]+=1
    return {"summary":{"reviewed_cases":len(rows),"candidate_edges_in_reviewed_cases":len(examined),
             "qwen_accepted_candidate_edges":len(accepted),"qwen_rejected_candidate_edges":len(examined-accepted),
             "note":"Agreement with Qwen is not factual accuracy."},
            "by_retrieval_method":dict(methods),"cases":rows,
            "limitations":["Qwen decisions on metadata are not independently verified ground truth.",
              "Only cases selected for Qwen review are counted; selection is not random.",
              "Card membership may imply extra pairs not present in candidate edges.",
              "Source text verification is required to estimate actual precision."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("graph",type=Path);p.add_argument("reviews",type=Path)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    out=audit(json.loads(a.graph.read_text()),json.loads(a.reviews.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("HYBRID_DISAGREEMENT",json.dumps(out["summary"]))
    print("METHODS",json.dumps(out["by_retrieval_method"]))
if __name__=="__main__":main()
