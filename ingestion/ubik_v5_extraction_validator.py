"""Validate independent axes and explicit within-source event relationships."""
NATURES={"container","fact"}
TEXT_ROLES={"narrated","referenced"}
POSITIONS={"support","criticism","neutral","mixed","unclear"}
def validate_extraction(answer,source):
    events=answer["events"];assignments=answer["assignments"]
    assert isinstance(events,list) and isinstance(assignments,list)
    ids=[e["id"] for e in events]
    assert len(ids)==len(set(ids)) and all(isinstance(x,str) and x for x in ids)
    idset=set(ids)
    for e in events:
        if e.get("event_nature") not in NATURES:raise ValueError("Invalid event_nature: "+str(e.get("event_nature")))
        if e.get("text_role") not in TEXT_ROLES:raise ValueError("Invalid text_role: "+str(e.get("text_role")))
        if not isinstance(e.get("event_part_of"),list):raise ValueError("Missing event_part_of")
        for rel in e["event_part_of"]:
            if not isinstance(rel,dict) or rel.get("event_id") not in idset or rel["event_id"]==e["id"]:
                raise ValueError("Invalid event_part_of target")
            if not isinstance(rel.get("evidence"),str) or not rel["evidence"].strip():
                raise ValueError("Missing part_of evidence")
    if {a["news_key"] for a in assignments}!={n["key"] for n in source["news"]}:
        raise ValueError("News assignment mismatch")
    for a in assignments:
        if a.get("primary_event_id") is not None and a["primary_event_id"] not in idset:
            raise ValueError("Invalid primary_event_id")
        for p in a.get("part_of",[]):
            target=p.get("event_id") if isinstance(p,dict) else p
            if target not in idset:raise ValueError("Invalid assignment part_of")
        for r in a.get("reacts_to",[]):
            if not isinstance(r,dict) or r.get("event_id") not in idset:
                raise ValueError("Invalid reacts_to")
    return True
