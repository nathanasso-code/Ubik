"""Render evidence-backed *review* cards, never automatically verified verdicts.

Consumes explicit human annotations and hash-consistent source texts. A passing
gate means only that passages are present in supplied texts, not that the
annotation is correct, the publisher is independent, or the claim is true.
"""
import argparse,json
from pathlib import Path
from ingestion.epistemic_evidence_gate import validate

def build_evidence_cards(reviews,sources,*,max_cards=24):
    if not 1<=max_cards<=100:raise ValueError("Invalid card budget")
    cards=[];rejections=[]
    for i,review in enumerate(reviews.get("reviews",[])):
        gate=validate(review,sources)
        if not gate["eligible_for_editorial_review"]:
            rejections.append({"index":i,"errors":gate["errors"]});continue
        evidence=[{"source_url":e["url"],"verbatim_quote":e["quote"]}
                  for e in review["evidence"]]
        cards.append({"type":"evidence_review_card","id":f"evidence-review-{i+1}",
                      "status":"editorial_review_required",
                      "proposed_relation":review["relation_type"],
                      "relation_is_verified":False,
                      "claim_is_verified":False,
                      "editorial_rationale_unverified":review.get("rationale"),
                      "compared_claims_unverified":review.get("compared_claims",[]),
                      "reviewer_id":review["reviewer_id"],
                      "sources":[review["left"]["url"],review["right"]["url"]],
                      "evidence":evidence,
                      "gate_result":"source_quote_consistency_only"})
        if len(cards)>=max_cards:break
    return {"schema_version":1,"purpose":"source_passage_editorial_review_cards",
            "cards":cards,"rejected":rejections,
            "automatic_publication":False,"verified_relations":0,
            "limitations":["Verbatim quotes and SHA-256 do not verify source authenticity or factual truth.",
                           "A proposed relation is a human annotation, not an accepted verdict.",
                           "No production publication or topic creation."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--reviews",type=Path,required=True)
    p.add_argument("--sources",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=build_evidence_cards(json.loads(a.reviews.read_text(encoding="utf-8")),
                                json.loads(a.sources.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cards":len(result["cards"]),"rejected":len(result["rejected"]),"verified":0}))
if __name__=="__main__":main()
