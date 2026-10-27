"""Frozen Ukraine v5 Sonnet cross-source judge; no new extraction."""
import json,os,urllib.request
from pathlib import Path
from ingestion.ubik_monarch_v5_rejudge_core import candidates,cautious_groups
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL,verify_response,verify_records
from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_part_of_validator_v5 import resolve_part_of
from ingestion.ubik_part_of_bridge_diagnostic import bridge_part_of_edges
ROOT=Path("data/ukraine-v5")
PROMPT="""Judge only the two supplied cross-source events, using their evidence. Output JSON with decision equivalent|distinct|uncertain|part_of, direction left_part_of_right|right_part_of_left|null, reason, detail_conflicts array. Equivalent means same concrete act or fact, not merely common topic. part_of requires a supported component-of relation, not mere reaction or proximity. Keep EU diesel supply agreement and US suspension of new sanctions distinct; generic sanctions easing may be ambiguous, so use uncertain if evidence insufficient. Distinguish Trump announcement from asserted agreement. Never invent missing evidence."""
def main():
 if os.getenv("UBIK_LLM_MODEL")!=EXPECTED_MODEL:raise RuntimeError("Wrong declared model")
 extraction=json.loads((ROOT/"v5-extraction.json").read_text())
 if extraction["model"]!=EXPECTED_MODEL or extraction["errors"]:raise RuntimeError("Invalid extraction")
 sources=extraction["sources"]
 pairs,scores,events=candidates(sources,k=5,soft_nature=True)
 out={"model":EXPECTED_MODEL,"extraction_artifact":"12719538526","candidate_pairs":len(pairs),"judgments":[],"usage":[],"errors":[]}
 def save():(ROOT/"v5-judge.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
 save()
 for left,right in pairs:
  try:
   request=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps({
    "model":EXPECTED_MODEL,"messages":[{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"left":events[left],"right":events[right]},ensure_ascii=False)}],
    "response_format":{"type":"json_object"},"max_tokens":3000}).encode(),
    headers={"Authorization":"Bearer "+os.environ["UBIK_LLM_API_KEY"],"Content-Type":"application/json"})
   with urllib.request.urlopen(request,timeout=240) as response:raw=json.load(response)
   audit=verify_response(raw,stage="judge",pair=[left,right])
   answer=json.loads(raw["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```").strip())
   if answer.get("decision") not in ("equivalent","distinct","uncertain","part_of"):raise ValueError("Invalid decision")
   if answer["decision"]=="part_of" and answer.get("direction") not in ("left_part_of_right","right_part_of_left"):raise ValueError("Invalid direction")
   out["judgments"].append({"left":left,"right":right,"similarity":scores[(left,right)],"result":answer})
   out["usage"].append(audit)
  except Exception as exc:
   out["errors"].append({"pair":[left,right],"error":str(exc)[:500]})
   save()
   raise
  save()
 out["cost_audit"]=verify_records(out["usage"])
 assembly=cautious_groups(events,out["judgments"],scores)
 out["assembly"]=assembly
 groups=assembly["groups"]
 lookup={e:"card:"+g[0] for g in groups for e in g}
 cards=[{"id":"card:"+g[0],"events":g,"source_ids":sorted({e.split(":")[0] for e in g})} for g in groups]
 relations=[]
 for s in sources:
  sid=s["source_id"]
  for e in s["answer"]["events"]:
   for rel in e.get("event_part_of",[]):
    a=lookup[sid+":"+e["id"]];b=lookup[sid+":"+rel["event_id"]]
    if a!=b:relations.append({"type":"part_of","source":a,"target":b,"origin":sid+":"+e["id"],"evidence":rel["evidence"]})
  for a in s["answer"]["assignments"]:
   primary=a.get("primary_event_id")
   if primary:
    for r in a.get("reacts_to",[]):
     x=lookup[sid+":"+primary];y=lookup[sid+":"+r["event_id"]]
     if x!=y:relations.append({"type":"reacts_to","source":x,"target":y,"origin":sid+":"+a["news_key"]})
 for j in assembly["part_of"]:
  a,b=j["left"],j["right"]
  child,parent=(a,b) if j["result"]["direction"]=="left_part_of_right" else (b,a)
  x,y=lookup[child],lookup[parent]
  if x!=y:relations.append({"type":"part_of","source":x,"target":y,"origin":"judge:"+a+"|"+b,"evidence":j["result"].get("reason","")})
 accepted,rejected=resolve_part_of([r for r in relations if r["type"]=="part_of"])
 relations=[r for r in relations if r["type"]=="reacts_to"]+accepted
 out["quarantined_relations"]=rejected
 out["bridge_diagnostic"]=bridge_part_of_edges(cards,relations)
 out["composition"]=compose_connected_v5(cards,relations,conflicts=rejected)
 out["relations"]=relations
 save()
 print(json.dumps({"pairs":len(pairs),"incidents":len(out["composition"]["incidents"]),"bridges":len(out["bridge_diagnostic"]),"cost":out["cost_audit"]}))
if __name__=="__main__":main()
