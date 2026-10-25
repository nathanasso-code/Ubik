"""Ubik v5: deterministic composition. A matrix requires >=2 distinct sources."""
from collections import defaultdict

def compose_v5(cards, relations, conflicts=()):
    by_id={c["id"]:dict(c) for c in cards}
    if len(by_id)!=len(cards): raise ValueError("Duplicate card id")
    parents=defaultdict(set); reactions=[]
    for r in relations:
        a,b,k=r["source"],r["target"],r["type"]
        if a not in by_id or b not in by_id: raise ValueError("Unknown endpoint")
        if a==b: raise ValueError("Self relation")
        if k=="part_of": parents[a].add(b)
        elif k=="reacts_to": reactions.append(r)
        else: raise ValueError("Unknown relation")
    def roots(cid,seen=frozenset()):
        if cid in seen: raise ValueError("Cyclic part_of")
        return set().union(*(roots(p,seen|{cid}) for p in parents[cid])) if parents[cid] else {cid}
    membership={cid:sorted(roots(cid)) for cid in by_id}
    matrices=[];single_source_groups=[];unresolved=[]
    for root in sorted({r for rs in membership.values() for r in rs}):
        members=sorted(cid for cid,rs in membership.items() if root in rs)
        source_ids=set().union(*(set(by_id[c].get("source_ids",[])) for c in members))
        # A shared topic or one source's substructure is never sufficient.
        links=[r for r in relations if r["type"]=="part_of" and r["source"] in members and r["target"] in members]
        reactions_to_group=[r for r in reactions if r["target"] in members]
        has_multisource_card=any(len(set(by_id[c].get("source_ids",[])))>=2 for c in members)
        has_multisource_relation=any(set(by_id[r["source"]].get("source_ids",[]))-
                                     set(by_id[r["target"]].get("source_ids",[])) or
                                     set(by_id[r["target"]].get("source_ids",[]))-
                                     set(by_id[r["source"]].get("source_ids",[]))
                                     for r in links+reactions_to_group)
        item={"anchor_card":root,"cards":members,"source_ids":sorted(source_ids),
              "part_of":links,"reactions":reactions_to_group}
        if len(source_ids)>=2 and (has_multisource_card or has_multisource_relation):
            matrices.append({"id":"matrix:"+root,**item})
        else: single_source_groups.append(item)
    return {"cards":cards,"matrices":matrices,"single_source_groups":single_source_groups,
            "memberships":membership,"reactions":reactions,"conflicts":list(conflicts),
            "new_llm_calls":0}
