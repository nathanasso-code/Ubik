"""Validate hierarchical topic categories proposed by an LLM.

Separate general subject, narrow subject and optional fine-grained tag.
Abstain rather than fabricate specificity. No model API or training required.
"""
from __future__ import annotations
import re
from typing import Any

def validate_hierarchy(proposal:dict[str,Any],source_text:str)->dict[str,Any]:
    if not isinstance(proposal,dict) or not source_text.strip():
        return {"accepted":False,"reason":"missing_input"}
    levels=proposal.get("levels")
    if not isinstance(levels,list) or not 1<=len(levels)<=4:
        return {"accepted":False,"reason":"invalid_depth"}
    normalized=[];seen=set()
    for level in levels:
        if not isinstance(level,dict):
            return {"accepted":False,"reason":"invalid_level"}
        label=level.get("label");evidence=level.get("evidence_quote")
        if not isinstance(label,str) or not re.fullmatch(r"[\wÀ-ÿ][\wÀ-ÿ ,/()'-]{1,79}",label.strip()):
            return {"accepted":False,"reason":"invalid_label"}
        if label.casefold().strip() in seen:
            return {"accepted":False,"reason":"duplicate_level"}
        if not isinstance(evidence,str) or not evidence.strip() or evidence.strip() not in source_text:
            return {"accepted":False,"reason":"ungrounded_category"}
        seen.add(label.casefold().strip())
        normalized.append({"depth":len(normalized)+1,"label":label.strip(),"evidence_quote":evidence.strip()})
    return {"accepted":True,"levels":normalized,"depth":len(normalized),
            "taxonomy_status":"proposed_for_review","automatically_published":False}
def schema()->dict[str,Any]:
    return {"type":"object","required":["levels"],"additionalProperties":False,
      "properties":{"levels":{"type":"array","minItems":1,"maxItems":4,"items":{"type":"object",
      "required":["label","evidence_quote"],"additionalProperties":False,
      "properties":{"label":{"type":"string"},"evidence_quote":{"type":"string"}}}}}}
