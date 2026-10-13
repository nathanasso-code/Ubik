"""A deterministic synthetic demonstration; not publisher evidence or a news result."""
import argparse,json
from pathlib import Path
from ingestion.epistemic_evidence_gate import fingerprint
from ingestion.evidence_review_cards import build_evidence_cards

def demonstration():
    a="The fictional regulator reported that electricity demand increased after the new facility opened."
    b="The fictional city authority reported that electricity demand did not increase after the facility opened."
    ua="https://example.org/synthetic-a";ub="https://example.net/synthetic-b"
    sources={ua:{"text":a,"sha256":fingerprint(a)},ub:{"text":b,"sha256":fingerprint(b)}}
    reviews={"reviews":[{"relation_type":"contradicts_claim","reviewer_id":"synthetic-fixture",
                          "left":{"url":ua},"right":{"url":ub},
                          "evidence":[{"url":ua,"quote":a},{"url":ub,"quote":b}],
                          "compared_claims":[a,b],
                          "rationale":"Synthetic statements disagree on demand after opening; editorial review still required."}]}
    result=build_evidence_cards(reviews,sources)
    result["synthetic_fixture_only"]=True
    result["real_publisher_articles_processed"]=0
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();result=demonstration()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"synthetic_review_cards":len(result["cards"]),"real_publisher_articles_processed":0}))
if __name__=="__main__":main()
