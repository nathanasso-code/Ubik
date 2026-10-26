"""Replay frozen monarch judgments and composition, zero model calls."""
import json
from pathlib import Path
from ingestion.ubik_monarch_v5_rejudge_core import cautious_groups
from ingestion.ubik_matrix_composer_v5 import compose_v5
from ingestion.ubik_part_of_validator_v5 import resolve_part_of
ROOT=Path("data/monarch-v5")
def main():
    previous=json.loads((ROOT/"rejudge-result.json").read_text())
    extraction=json.loads((ROOT/"frozen-result.json").read_text())
    events={s["source_id"]+":"+e["id"]:e for s in extraction["sources"] for e in s["answer"]["events"]}
    scores={tuple(sorted((j["left"],j["right"]))):j["similarity"] for j in previous["judgments"]}
    assembly=cautious_groups(events,previous["judgments"],scores)
    groups=assembly["groups"]
    lookup={e:"card:"+g[0] for g in groups for e in g}
    cards=[{"id":"card:"+g[0],"events":g,"source_ids":sorted({e.split(":")[0] for e in g}),
            "independent_origin_ids":["probable-shared-monarch-origin"]} for g in groups]
    relations=[]
    for source in extraction["sources"]:
        sid=source["source_id"]
        for a in source["answer"]["assignments"]:
            if not a.get("primary_event_id"):continue
            for p in a.get("part_of",[]):
                parent=p["event_id"] if isinstance(p,dict) else p
                x=lookup[sid+":"+a["primary_event_id"]];y=lookup[sid+":"+parent]
                if x!=y:relations.append({"type":"part_of","source":x,"target":y,"origin":"extraction:"+sid})
    for j in assembly["part_of"]:
        a,b=j["left"],j["right"]
        child,parent=(a,b) if j["result"]["direction"]=="left_part_of_right" else (b,a)
        x,y=lookup[child],lookup[parent]
        if x!=y:relations.append({"type":"part_of","source":x,"target":y,"origin":"judge:"+a+":"+b})
    relations=list({(r["source"],r["target"],r["origin"]):r for r in relations}.values())
    accepted,rejected=resolve_part_of(relations)
    out={"frozen_extraction_run":40415277851,"reused_judgment_run":40421847220,
         "new_llm_calls":0,"candidate_pairs":previous["candidate_pairs"],
         "all_possible_pairs":previous["all_possible_pairs"],
         "judgments":previous["judgments"],"assembly":assembly,
         "quarantined_relations":rejected,"accepted_relations":accepted}
    out["composition"]=compose_v5(cards,accepted,conflicts=rejected)
    (ROOT/"recomposed-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({"candidate_pairs":out["candidate_pairs"],"groups":len(groups),
        "quarantined":len(rejected),"incidents":len(out["composition"]["incidents"]),
        "matrices":len(out["composition"]["matrices"]),"new_llm_calls":0}))
if __name__=="__main__":main()
