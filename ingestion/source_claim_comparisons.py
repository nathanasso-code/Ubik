"""Generate claim comparison worksheets from source-text candidates and frozen semantic pairs.

This is an evidence assembly tool, not an automated contradiction classifier.
"""
import argparse,json
from pathlib import Path

def compare_candidates(review,claim_report,*,max_pairs=24):
    claims={x["url"]:x for x in claim_report.get("sources",[])}
    comparisons=[]
    for pair in review.get("selected",[]):
        left=pair.get("left") or {};right=pair.get("right") or {}
        a=claims.get(left.get("url"),{}).get("candidates",[])
        b=claims.get(right.get("url"),{}).get("candidates",[])
        if not a or not b:continue
        comparisons.append({"frozen_rank":pair.get("frozen_rank"),
                            "left":{"url":left["url"],"title":left.get("title"),"claim_candidates":a},
                            "right":{"url":right["url"],"title":right.get("title"),"claim_candidates":b},
                            "review_question":"Do any two exact quoted assertions refer to the same agent, action, target, time and scope?",
                            "relation_type":"insufficient_evidence",
                            "review_status":"requires_claim_alignment_and_editorial_review",
                            "automatic_entailment":False,"verified":False})
        if len(comparisons)>=max_pairs:break
    return {"schema_version":1,"purpose":"unverified_claim_comparison_worksheets",
            "comparisons":comparisons,"published":False,"automatic_topic_creation":False,
            "limitations":["No semantic alignment, contradiction, truth or causality was inferred.",
                           "Only exact source sentences from hash-validated text are eligible.",
                           "Unreviewed candidate sentences can be questions, opinions or quotations."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--review",type=Path,required=True)
    p.add_argument("--claims",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=compare_candidates(json.loads(a.review.read_text(encoding="utf-8")),
                              json.loads(a.claims.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"comparisons":len(result["comparisons"]),"verified":0}))
if __name__=="__main__":main()
