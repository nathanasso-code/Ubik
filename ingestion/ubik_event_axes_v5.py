"""Closed v5 event axes. Legacy mapping is explicit and auditable, never an LLM re-extraction."""
NATURES={"container","fact"}
TEXT_ROLES={"narrated","referenced"}
LEGACY_CONTAINER={"project","study","law","product","policy"}
LEGACY_FACT={"action","technological_innovation","finding","process","state","discovery","observation","property"}
def normalize_event(e):
    result=dict(e)
    if "event_nature" not in result:
        role=str(e.get("role","")).strip().lower()
        if role in LEGACY_CONTAINER:result["event_nature"]="container"
        elif role in LEGACY_FACT:result["event_nature"]="fact"
        else:raise ValueError("Unknown legacy nature role: "+repr(role))
        result["event_nature_provenance"]="legacy_role_mapping"
    if "text_role" not in result:
        result["text_role"]="narrated" if str(e.get("context_signal","")).lower() in ("primary","general","concrete_tracking_project","method_implementation","enabling_technology","migration_route_finding","habitat_finding","data_collection_method") else "referenced"
        result["text_role_provenance"]="legacy_heuristic_unverified"
    if result["event_nature"] not in NATURES:raise ValueError("Invalid event_nature")
    if result["text_role"] not in TEXT_ROLES:raise ValueError("Invalid text_role")
    return result
