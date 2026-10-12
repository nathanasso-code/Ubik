"""Strict source-text evidence gates for editorial epistemic links.

This module does not fetch articles, infer claims or declare truth. It validates
human-annotated source passages against supplied immutable source text and
rejects unsupported causal/contradiction labels.
"""
import argparse,hashlib,json,re
from pathlib import Path

RELATIONS={"same_event","related_distinct_events","shared_context","supports_claim",
           "contradicts_claim","source_asserts_causal_link","spurious","insufficient_evidence"}
EPISTEMIC={"supports_claim","contradicts_claim","source_asserts_causal_link"}

def fingerprint(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate(review,sources):
    errors=[]
    relation=review.get("relation_type")
    if relation not in RELATIONS:errors.append("unknown_relation_type")
    if review.get("reviewer_id") in (None,""):errors.append("reviewer_required")
    evidence=review.get("evidence") or []
    if not isinstance(evidence,list):errors.append("evidence_must_be_list");evidence=[]
    urls={x.get("url") for x in (review.get("left") or {},review.get("right") or {})}
    valid_evidence=[]
    for index,e in enumerate(evidence):
        if not isinstance(e,dict):errors.append(f"evidence_{index}_invalid");continue
        url=e.get("url");quote=e.get("quote")
        source=sources.get(url)
        if url not in urls or not isinstance(source,dict):
            errors.append(f"evidence_{index}_unmatched_url");continue
        body=source.get("text")
        if not isinstance(body,str) or not isinstance(quote,str) or len(quote.strip())<20:
            errors.append(f"evidence_{index}_missing_source_text_or_quote");continue
        if quote not in body:
            errors.append(f"evidence_{index}_quote_not_found_verbatim");continue
        if source.get("sha256")!=fingerprint(body):
            errors.append(f"evidence_{index}_source_hash_mismatch");continue
        valid_evidence.append(url)
    if relation in EPISTEMIC:
        if set(valid_evidence)!=urls:
            errors.append("epistemic_relation_requires_both_source_passages")
        claims=review.get("compared_claims")
        if not isinstance(claims,list) or len(claims)!=2 or any(not isinstance(x,str) or len(x.strip())<15 for x in claims):
            errors.append("two_explicit_compared_claims_required")
        if not isinstance(review.get("rationale"),str) or len(review["rationale"].strip())<30:
            errors.append("substantive_rationale_required")
    elif relation in {"same_event","related_distinct_events"}:
        if set(valid_evidence)!=urls:
            errors.append("event_relation_requires_both_source_passages")
    return {"eligible_for_editorial_review":not errors,
            "automatic_publication":False,"verified_as_true":False,
            "errors":errors,"relation_type":relation,
            "source_passages_matched":len(valid_evidence)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--review",type=Path,required=True)
    p.add_argument("--sources",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=validate(json.loads(a.review.read_text(encoding="utf-8")),
                    json.loads(a.sources.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result))
if __name__=="__main__":main()
