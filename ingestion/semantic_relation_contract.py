"""Ubik semantic relation contract: meaning and relations, not truth verdicts.

Conservative deterministic validation of a proposed LLM analysis.
This does not call an LLM or infer relations by itself.
"""
from __future__ import annotations
import json
from typing import Any

EVENT={"same_event","same_topic_different_event","related_development","unrelated","uncertain"}
RELATION={"restates","adds_detail","provides_context","updates","supports","challenges","contrasts_perspective","different_focus","uncertain"}
def validate_relation(proposal:dict[str,Any],sources:dict[str,str])->dict[str,Any]:
    """Return an evidence-grounded proposal or abstain, preserving source provenance."""
    ids=(proposal.get("document_a_id"),proposal.get("document_b_id"))
    if not all(isinstance(x,str) and x in sources for x in ids) or ids[0]==ids[1]:
        return {"accepted":False,"reason":"unknown_or_duplicate_document","decision":"abstain"}
    if proposal.get("event_relation") not in EVENT or proposal.get("semantic_relation") not in RELATION:
        return {"accepted":False,"reason":"invalid_relation","decision":"abstain"}
    quotes=proposal.get("evidence",[])
    if not isinstance(quotes,list) or len(quotes)<2:
        return {"accepted":False,"reason":"insufficient_evidence","decision":"abstain"}
    seen=set()
    for q in quotes:
        if not isinstance(q,dict) or q.get("document_id") not in ids or not isinstance(q.get("quote"),str):
            return {"accepted":False,"reason":"invalid_evidence","decision":"abstain"}
        quote=q["quote"].strip()
        if not quote or quote not in sources[q["document_id"]]:
            return {"accepted":False,"reason":"ungrounded_quote","decision":"abstain"}
        seen.add(q["document_id"])
    if seen!=set(ids):
        return {"accepted":False,"reason":"missing_document_evidence","decision":"abstain"}
    return {"accepted":True,"decision":"candidate_for_review",
            "event_relation":proposal["event_relation"],"semantic_relation":proposal["semantic_relation"],
            "document_a_id":ids[0],"document_b_id":ids[1],"evidence":quotes,
            "asserts_factual_truth":False,"automatic_merge_allowed":False}
def json_schema()->dict[str,Any]:
    return {"type":"object","additionalProperties":False,
        "required":["document_a_id","document_b_id","event_relation","semantic_relation","evidence"],
        "properties":{"document_a_id":{"type":"string"},"document_b_id":{"type":"string"},
          "event_relation":{"type":"string","enum":sorted(EVENT)},
          "semantic_relation":{"type":"string","enum":sorted(RELATION)},
          "evidence":{"type":"array","minItems":2,"items":{"type":"object","additionalProperties":False,
             "required":["document_id","quote"],"properties":{"document_id":{"type":"string"},"quote":{"type":"string"}}}}}}
if __name__=="__main__":print(json.dumps(json_schema(),ensure_ascii=False,indent=2))
