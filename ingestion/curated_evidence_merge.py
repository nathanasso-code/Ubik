"""Conservative evidence packet merger: chronology, source independence and taxonomy.

Accepts curated source observations with explicit provenance. Does not infer
relations from embeddings and does not turn syndicated reports into independent votes.
"""
from collections import defaultdict

def assemble_case(observations):
    if not observations:raise ValueError("No observations")
    events={x["event_key"] for x in observations}
    if len(events)!=1:raise ValueError("Do not merge distinct event keys")
    for x in observations:
        if not all(x.get(k) for k in ("url","publisher","observed_at","claim","evidence_excerpt","origin_group","event_key")):
            raise ValueError("Missing provenance")
        if len(x["evidence_excerpt"].split())>25:raise ValueError("Excerpt exceeds short quotation budget")
    ordered=sorted(observations,key=lambda x:x["observed_at"])
    by_claim=defaultdict(list)
    for x in ordered:by_claim[x["claim_key"]].append(x)
    changes=[];conflicts=[]
    for key,rows in by_claim.items():
        values={str(x["value"]) for x in rows}
        if len(values)>1:
            times={x["observed_at"] for x in rows}
            if len(times)>1:
                changes.append({"claim_key":key,"status":"potential_temporal_update",
                                "values":[{"value":x["value"],"observed_at":x["observed_at"],"url":x["url"]} for x in rows]})
            else:
                conflicts.append({"claim_key":key,"status":"unresolved_same_timestamp_difference",
                                  "source_urls":[x["url"] for x in rows]})
    return {"schema_version":1,"event_key":ordered[0]["event_key"],
            "source_count":len({x["url"] for x in ordered}),
            "declared_origin_groups":len({x["origin_group"] for x in ordered}),
            "independent_origin_count_verified":None,
            "observations":ordered,"potential_updates":changes,
            "unresolved_differences":conflicts,
            "same_event_verified":False,"truth_verified":False,
            "editorial_status":"requires_editorial_review",
            "publication_approved":False,
            "limitations":["Event key and origin groups are curator-provided, not independently authenticated.",
                           "Different timestamps suggest possible updates, not proof of temporal resolution.",
                           "A common agency origin must not be counted as independent corroboration."]}

def categorize(case):
    # Curated closed taxonomy, NOT model-generated topic proliferation.
    key=case["event_key"].lower()
    if "hurricane" in key or "storm" in key:
        return {"section":"Pulse","category":"Ambiente e clima",
                "tags":["eventi meteorologici estremi","Messico","protezione civile"],
                "classification":"curated_rule","new_topic_created":False}
    return {"section":"Press","category":"Da classificare","tags":[],
            "classification":"abstained","new_topic_created":False}
