"""Zero-LLM uniform recomposition of frozen original and concise Sonnet judgments."""
import json
from pathlib import Path
from ingestion.ubik_monarch_v5_rejudge_core import cautious_groups
from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_part_of_validator_v5 import resolve_part_of
root=Path("data/ukraine-sonnet-uniform");root.mkdir(parents=True,exist_ok=True)
ex=json.loads((root/"v5-extraction.json").read_text())
orig=json.loads((root/"v5-judge.json").read_text())
conc=json.loads((root/"sonnet-concise-result.json").read_text())
assert len(orig["judgments"])==len(conc["judgments"])==131
assert [(j["left"],j["right"]) for j in orig["judgments"]]==[(j["left"],j["right"]) for j in conc["judgments"]]
events={s["source_id"]+":"+e["id"]:e for s in ex["sources"] for e in s["answer"]["events"]}
scores={(j["left"],j["right"]):j["similarity"] for j in orig["judgments"]}
def build(judgments):
 assembly=cautious_groups(events,judgments,scores)
 groups=assembly["groups"]
 lookup={e:"card:"+g[0] for g in groups for e in g}
 cards=[{"id":"card:"+g[0],"events":g,"source_ids":sorted({e.split(":")[0] for e in g})} for g in groups]
 relations=[]
 for s in ex["sources"]:
  sid=s["source_id"]
  for e in s["answer"]["events"]:
   for rel in e.get("event_part_of",[]):
    a=lookup[sid+":"+e["id"]];b=lookup[sid+":"+rel["event_id"]]
    if a!=b:relations.append({"type":"part_of","source":a,"target":b,"origin":sid+":"+e["id"],"evidence":rel["evidence"]})
  for a in s["answer"]["assignments"]:
   p=a.get("primary_event_id")
   if p:
    for t in a.get("reacts_to",[]):
     x=lookup[sid+":"+p];y=lookup[sid+":"+t["event_id"]]
     if x!=y:relations.append({"type":"reacts_to","source":x,"target":y,"origin":sid+":"+a["news_key"]})
 for j in assembly["part_of"]:
  a,b=j["left"],j["right"]
  child,parent=(a,b) if j["result"]["direction"]=="left_part_of_right" else (b,a)
  x,y=lookup[child],lookup[parent]
  if x!=y:relations.append({"type":"part_of","source":x,"target":y,"origin":"judge:"+a+"|"+b,"evidence":j["result"].get("reason","")})
 accepted,rejected=resolve_part_of([r for r in relations if r["type"]=="part_of"])
 relations=[r for r in relations if r["type"]=="reacts_to"]+accepted
 return {"assembly":assembly,"relations":relations,"quarantined_relations":rejected,"composition":compose_connected_v5(cards,relations,conflicts=rejected)}
a=build(orig["judgments"]);b=build(conc["judgments"])
def groups(x):return [sorted(g) for g in x["assembly"]["groups"]]
def summary(x):
 c=x["composition"]
 return {"cards":len(x["assembly"]["groups"]),"incidents":len(c["incidents"]),"matrices":len(c["matrices"]),"topic_cards":len(c.get("topic_cards",[])),"single_source_groups":len(c.get("single_source_groups",[]))}
ag={tuple(g) for g in groups(a)};bg={tuple(g) for g in groups(b)}
diff=[{"pair":[x["left"],x["right"]],"original":x["result"]["decision"],"concise":y["result"]["decision"]} for x,y in zip(orig["judgments"],conc["judgments"]) if x["result"]["decision"]!=y["result"]["decision"]]
out={"method":"identical current composer, identical frozen extraction and ordered pairs, no model calls","original":a,"concise":b,"summary":{"original":summary(a),"concise":summary(b),"groups_only_original":[list(g) for g in sorted(ag-bg)],"groups_only_concise":[list(g) for g in sorted(bg-ag)],"changed_verdicts":diff},"weighted_gold_score":"not_scored_without_extraction_blind_gold_alignment"}
(root/"uniform-comparison.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out["summary"]))
