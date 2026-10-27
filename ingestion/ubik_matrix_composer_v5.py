"""Ubik v5: uniform referent-centered incidents; source count controls presentation only."""
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
    matrices=[];single_source_groups=[];incidents=[];unresolved=[]
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
        independent_ids=sorted(set(by_id[c].get("independent_origin_ids",[]) [0] if len(by_id[c].get("independent_origin_ids",[]))==1 else s for c in members for s in (by_id[c].get("independent_origin_ids") or by_id[c].get("source_ids",[]))))
        item["independent_origin_ids"]=independent_ids
        item["presentation"]="matrix" if len(independent_ids)>=2 and (has_multisource_card or has_multisource_relation) else "single_source"
        incidents.append({"id":"incident:"+root,**item})
        if item["presentation"]=="matrix":
            matrices.append({"id":"matrix:"+root,**item})
        else: single_source_groups.append(item)
    return {"cards":cards,"incidents":incidents,"matrices":matrices,"single_source_groups":single_source_groups,
            "memberships":membership,"reactions":reactions,"conflicts":list(conflicts),
            "new_llm_calls":0}


def compose_connected_v5(cards, relations, context_card_ids=(), conflicts=()):
    """Structural components with reactions attached; isolated cards stay in Topic.

    A reaction cannot bridge two structurally separate incidents. No LLM calls.
    """
    by_id={c["id"]:dict(c) for c in cards}
    if len(by_id)!=len(cards):raise ValueError("Duplicate card id")
    context=set(context_card_ids)
    if context-set(by_id):raise ValueError("Unknown context card")
    adjacency={cid:set() for cid in by_id}
    reactions=[]
    for r in relations:
        a,b=r["source"],r["target"]
        if a not in by_id or b not in by_id:raise ValueError("Unknown endpoint")
        if a==b:continue
        if r["type"]=="part_of":
            adjacency[a].add(b);adjacency[b].add(a)
        elif r["type"]=="reacts_to":reactions.append(r)
        else:raise ValueError("Unknown relation")
    components=[];owner={};seen=set()
    for cid in sorted(by_id):
        if cid in seen:continue
        component=set();stack=[cid]
        while stack:
            node=stack.pop()
            if node in component:continue
            component.add(node);stack.extend(adjacency[node]-component)
        seen.update(component)
        idx=len(components);components.append(component)
        for node in component:owner[node]=idx
    outgoing=defaultdict(set)
    for r in reactions:
        if owner[r["source"]]!=owner[r["target"]]:
            outgoing[owner[r["source"]]].add(owner[r["target"]])
    attached={};ambiguous=[]
    for idx,targets in sorted(outgoing.items()):
        if len(components[idx])!=1:continue
        if len(targets)!=1:
            ambiguous.append({"cards":sorted(components[idx]),"target_components":sorted(targets)})
            continue
        dest=next(iter(targets));visited={idx}
        while dest in outgoing and len(components[dest])==1 and len(outgoing[dest])==1 and dest not in visited:
            visited.add(dest);dest=next(iter(outgoing[dest]))
        if dest not in visited:attached[idx]=dest
    grouped=defaultdict(set)
    for idx,component in enumerate(components):
        grouped[attached.get(idx,idx)].update(component)
    incidents=[];matrices=[];single=[];membership={};topic_cards=[]
    for idx,members_set in sorted(grouped.items()):
        active=members_set-context
        if not active:continue
        members=sorted(members_set)
        part=[r for r in relations if r["type"]=="part_of" and r["source"] in members_set and r["target"] in members_set]
        react=[r for r in reactions if r["source"] in members_set and r["target"] in members_set]
        if len(members)==1 and not part and not react:
            topic_cards.extend(members);continue
        # Only target/structural cards count toward matrix corroboration.
        reaction_only={r["source"] for r in react if not adjacency[r["source"]]}
        structural=members_set-reaction_only or members_set
        origins=sorted(set(o for x in structural for o in (by_id[x].get("independent_origin_ids") or by_id[x].get("source_ids",[]))))
        all_origins=sorted(set(o for x in members for o in (by_id[x].get("independent_origin_ids") or by_id[x].get("source_ids",[]))))
        sources=sorted(set(s for x in members for s in by_id[x].get("source_ids",[])))
        cross=any(len(set(by_id[x].get("source_ids",[])))>=2 for x in structural) or any(
            set(by_id[r["source"]].get("source_ids",[]))!=set(by_id[r["target"]].get("source_ids",[])) for r in part)
        presentation="matrix" if len(origins)>=2 and cross else "single_source"
        anchor=min(structural)
        item={"id":"incident:"+anchor,"anchor_card":anchor,"cards":members,
              "source_ids":sources,"independent_origin_ids":all_origins,
              "part_of":part,"reactions":react,"presentation":presentation,
              "origin_verification":"provisional"}
        incidents.append(item)
        for x in members:membership[x]=[item["id"]]
        if presentation=="matrix":matrices.append(item)
        else:single.append(item)
    return {"cards":cards,"incidents":incidents,"matrices":matrices,
            "single_source_groups":single,"memberships":membership,
            "topic_cards":sorted(topic_cards),"ambiguous_reaction_attachments":ambiguous,
            "context_cards":sorted(context-set(membership)),
            "conflicts":list(conflicts),"new_llm_calls":0}


def display_part_of_edges(relations):
    """One display edge per child-parent pair; preserve all evidence, reduce transitive edges.
    This is a VIEW only. Never use it to count independent confirmations.
    """
    by_pair={}
    for r in relations:
        if r["type"]!="part_of":continue
        key=(r["source"],r["target"])
        by_pair.setdefault(key,[]).append(r)
    graph=defaultdict(set)
    for child,parent in by_pair:graph[child].add(parent)
    def alternative_path(child,parent):
        todo=list(graph[child]-{parent});visited=set()
        while todo:
            n=todo.pop()
            if n==parent:return True
            if n in visited:continue
            visited.add(n);todo.extend(graph[n]-visited)
        return False
    return [{"source":child,"target":parent,"type":"part_of",
             "evidence_count":len(provenance),
             "provenance":provenance}
            for (child,parent),provenance in sorted(by_pair.items())
            if not alternative_path(child,parent)]
