"""Rejudge archived monarch v5 events only. Never repeat extraction."""
import json,os,sys
from pathlib import Path
from ingestion.ubik_monarch_v5_pilot import ask,save,JUDGE,ROOT
from ingestion.ubik_monarch_v5_rejudge_core import candidates,cautious_groups
from ingestion.ubik_matrix_composer_v5 import compose_v5
from ingestion.ubik_part_of_validator_v5 import resolve_part_of

JUDGE_V2="""Compare two event records from different sources. Return JSON only:
{decision:'equivalent'|'distinct'|'uncertain'|'part_of',
direction:'left_part_of_right'|'right_part_of_left'|null,
reason:string,detail_conflicts:[]}.
Equivalent requires the SAME concrete fact, not project vs detail. part_of
means one fact is a component of the other, with direction. An additional
detail is not necessarily a distinct event; record it in the reason. Do not
infer evidence not present in records. Missing information is not a conflict."""

def main():
    prior=json.loads((ROOT/"frozen-result.json").read_text())
    assert len(prior["sources"])==2
    sources=prior["sources"]
    pairs,scores,events=candidates(sources,k=5)
    out={"method":"frozen_v5_extraction_e5_small_top5_role_filtered",
         "source_run":40415277851,"sources_reused":[s["source_id"] for s in sources],
         "extraction_calls":0,"candidate_pairs":len(pairs),
         "all_possible_pairs":len(sources[0]["answer"]["events"])*len(sources[1]["answer"]["events"]),
         "judgments":[],"usage":[],"errors":[]}
    (ROOT/"rejudge-result.json").write_text(json.dumps(out,indent=2))
    for left,right in pairs:
        try:
            answer,usage=ask(JUDGE_V2,{"left":events[left],"right":events[right]})
            assert answer.get("decision") in ("equivalent","distinct","uncertain","part_of")
            if answer["decision"]=="part_of":
                assert answer.get("direction") in ("left_part_of_right","right_part_of_left")
            out["judgments"].append({"left":left,"right":right,"similarity":scores[(left,right)],
                                     "result":answer})
            out["usage"].append({"pair":[left,right],"usage":usage})
        except Exception as e:
            out["errors"].append({"pair":[left,right],"error":str(e)[:300]})
        (ROOT/"rejudge-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
    if out["errors"]:raise RuntimeError("Judge failures; do not claim completion")
    out["assembly"]=cautious_groups(events,out["judgments"],scores)
    groups=out["assembly"]["groups"]
    lookup={e:"card:"+g[0] for g in groups for e in g}
    cards=[{"id":"card:"+g[0],"events":g,
            "source_ids":sorted({e.split(":")[0] for e in g}),
            "independent_origin_ids":["shared-monarch-content"]} for g in groups]
    relations=[]
    for s in sources:
        sid=s["source_id"]
        for a in s["answer"]["assignments"]:
            if not a.get("primary_event_id"):continue
            for parent in a.get("part_of",[]):
                x=lookup[sid+":"+a["primary_event_id"]];y=lookup[sid+":"+parent]
                if x!=y and {"type":"part_of","source":x,"target":y} not in relations:
                    relations.append({"type":"part_of","source":x,"target":y})
    for j in out["assembly"]["part_of"]:
        a,b=j["left"],j["right"]
        if j["result"]["direction"]=="left_part_of_right":child,parent=a,b
        else:child,parent=b,a
        x,y=lookup[child],lookup[parent]
        if x!=y and {"type":"part_of","source":x,"target":y} not in relations:
            relations.append({"type":"part_of","source":x,"target":y})
    accepted,rejected=resolve_part_of(relations)
    out["quarantined_relations"]=rejected
    out["composition"]=compose_v5(cards,accepted,conflicts=rejected)
    (ROOT/"rejudge-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({"candidate_pairs":len(pairs),"equivalent":sum(j["result"]["decision"]=="equivalent" for j in out["judgments"]),
     "part_of":sum(j["result"]["decision"]=="part_of" for j in out["judgments"]),
     "groups":len(groups),"incidents":len(out["composition"]["incidents"]),
     "matrices":len(out["composition"]["matrices"]),"usage":out["usage"]},ensure_ascii=False))
if __name__=="__main__":main()
