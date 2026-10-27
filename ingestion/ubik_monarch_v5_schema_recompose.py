"""Zero-LLM deterministic replay of schema-v5 monarch judgments."""
import json
from pathlib import Path
from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_part_of_validator_v5 import resolve_part_of
ROOT=Path("data/monarch-v5")
def canonical(s):
    sid=s["source_id"];ans=s["answer"]
    remap={e["id"]:(e["id"][len(sid)+1:] if e["id"].startswith(sid+":") else e["id"]) for e in ans["events"]}
    for e in ans["events"]:
        e["id"]=remap[e["id"]]
        for r in e["event_part_of"]:r["event_id"]=remap[r["event_id"]]
    for a in ans["assignments"]:
        if a.get("primary_event_id"):a["primary_event_id"]=remap[a["primary_event_id"]]
    return s
def replay(extraction,prior):
    sources=[canonical(s) for s in extraction["sources"]]
    events={s["source_id"]+":"+e["id"]:e for s in sources for e in s["answer"]["events"]}
    eq=[j for j in prior["judgments"] if j["result"]["decision"]=="equivalent"]
    def priority(j):
        same=events[j["left"]]["event_nature"]==events[j["right"]]["event_nature"]
        return (-int(same),-float(j["similarity"]),j["left"],j["right"])
    groups=[{eid} for eid in sorted(events)]
    conflicts=[]
    for j in sorted(eq,key=priority):
        left,right=j["left"],j["right"]
        ga=next(g for g in groups if left in g)
        gb=next(g for g in groups if right in g)
        if ga is gb:continue
        merged=ga|gb
        if len({x.split(":")[0] for x in merged})!=len(merged):
            conflicts.append({"left":left,"right":right,"reason":"competing_equivalence",
                              "similarity":j["similarity"],"decision":"equivalent",
                              "visibility":"related_not_confirmed"})
            continue
        groups.remove(ga);groups.remove(gb);groups.append(merged)
    groups=sorted(groups,key=lambda g:sorted(g))
    lookup={eid:"card:"+sorted(g)[0] for g in groups for eid in g}
    cards=[{"id":"card:"+sorted(g)[0],"events":sorted(g),
            "source_ids":sorted({e.split(":")[0] for e in g}),
            "independent_origin_ids":["shared-monarch-content"]} for g in groups]
    relations=[]
    for s in sources:
        sid=s["source_id"]
        for e in s["answer"]["events"]:
            for r in e.get("event_part_of",[]):
                a,b=lookup[sid+":"+e["id"]],lookup[sid+":"+r["event_id"]]
                if a!=b:relations.append({"type":"part_of","source":a,"target":b,
                   "origin":"extraction:"+sid+":"+e["id"],"evidence":r["evidence"]})
    for j in prior["judgments"]:
        if j["result"]["decision"]!="part_of":continue
        a,b=j["left"],j["right"]
        child,parent=(a,b) if j["result"]["direction"]=="left_part_of_right" else (b,a)
        x,y=lookup[child],lookup[parent]
        if x!=y:relations.append({"type":"part_of","source":x,"target":y,
            "origin":"judge:"+a+":"+b,"evidence":j["result"].get("reason","")})
    accepted,rejected=resolve_part_of(relations)
    context_events=set()
    duplicate=[]
    for s in sources:
        sid=s["source_id"];seen={}
        for a in s["answer"]["assignments"]:
            p=a.get("primary_event_id")
            if p:
                if p in seen:duplicate.append({"source_id":sid,"event_id":p,"news":[seen[p],a["news_key"]]})
                else:seen[p]=a["news_key"]
            if a.get("context_only") and p:context_events.add(sid+":"+p)
    # Only wholly context-derived cards may be suppressed.
    context_cards={lookup[eid] for eid in context_events if all(
        member in context_events for member in next(g for g in groups if eid in g))}
    composition=compose_connected_v5(cards,accepted,context_cards,conflicts)
    for conflict in conflicts:
        conflict["left_card"]=lookup[conflict["left"]]
        conflict["right_card"]=lookup[conflict["right"]]
    return {"source_run":40466373012,"new_llm_calls":0,
        "judgments_reused":len(prior["judgments"]),"candidate_pairs_reused":prior["candidate_pairs"],
        "identity_groups":[sorted(g) for g in groups],
        "identity_conflicts":conflicts,"accepted_relations":accepted,
        "quarantined_relations":rejected,"duplicate_primary_errors":duplicate,
        "composition":composition}
def main():
    extraction=json.loads((ROOT/"schema-extraction-result.json").read_text())
    prior=json.loads((ROOT/"schema-rejudge-result.json").read_text())
    out=replay(extraction,prior)
    (ROOT/"schema-recomposed-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({"incidents":len(out["composition"]["incidents"]),
        "contexts":len(out["composition"]["context_cards"]),
        "cards":len(out["composition"]["cards"]),
        "identity_conflicts":len(out["identity_conflicts"]),
        "duplicate_primary_errors":len(out["duplicate_primary_errors"]),
        "quarantined":len(out["quarantined_relations"]),
        "llm_calls":0}))
if __name__=="__main__":main()
