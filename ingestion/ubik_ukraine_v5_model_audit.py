"""Fail-closed model and cost audit for controlled Ukraine v5 calls."""
import json
EXPECTED_MODEL="anthropic/claude-sonnet-5.5"
def verify_response(response,requested_model=EXPECTED_MODEL,stage=None,source_id=None,pair=None):
    if requested_model!=EXPECTED_MODEL:
        raise RuntimeError(f"Ukraine v5 requires {EXPECTED_MODEL}; requested {requested_model}")
    actual=response.get("model")
    if actual!=EXPECTED_MODEL:
        raise RuntimeError(f"Model mismatch: expected {EXPECTED_MODEL}, returned {actual!r}")
    usage=response.get("usage")
    if not isinstance(usage,dict) or not isinstance(usage.get("prompt_tokens"),int) or not isinstance(usage.get("completion_tokens"),int):
        raise RuntimeError("Missing comparable usage: abort instead of silently counting zero cost")
    record={"stage":stage,"source_id":source_id,"pair":pair,"requested_model":requested_model,
        "returned_model":actual,"usage":usage,"cost_usd":usage.get("cost"),
        "cost_status":"reported" if isinstance(usage.get("cost"),(int,float)) else "unreported"}
    return record
def verify_records(records):
    for record in records:
        if record["requested_model"]!=EXPECTED_MODEL or record["returned_model"]!=EXPECTED_MODEL:
            raise RuntimeError("Mixed-model run is invalid")
    return {"model":EXPECTED_MODEL,"calls":len(records),
      "total_reported_cost_usd":sum(r["cost_usd"] for r in records if isinstance(r["cost_usd"],(int,float))),
      "cost_complete":all(r["cost_status"]=="reported" for r in records)}
