"""Frozen v5 extraction and frozen 131 pairs; DeepSeek-only judge substitution."""
import json, os, urllib.request, time
from pathlib import Path
from ingestion.ubik_ukraine_v5_judge import PROMPT
from ingestion.ubik_monarch_v5_rejudge_core import cautious_groups
from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_part_of_validator_v5 import resolve_part_of

root=Path("data/ukraine-deepseek-v41-flash"); root.mkdir(parents=True,exist_ok=True)
ex=json.loads((root/"v5-extraction.json").read_text())
baseline=json.loads((root/"v5-judge.json").read_text())
assert len(baseline["judgments"])==131 and not baseline["errors"]
assert sum(len(s["answer"]["events"]) for s in ex["sources"])==38
events={s["source_id"]+":"+e["id"]:e for s in ex["sources"] for e in s["answer"]["events"]}
pairs=[(j["left"],j["right"]) for j in baseline["judgments"]]
assert len(set(pairs))==131 and all(a in events and b in events for a,b in pairs)
model="deepseek/deepseek-v4.1-flash-1017"
out={"model":model,"extraction_model":ex["model"],"baseline_artifact":"12725256478","extraction_artifact":"12719538526","candidate_pairs":131,"judgments":[],"usage":[],"invalid_after_retry":[],"errors":[]}
def save(): (root/"deepseek-v41-flash-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
save()
for idx,(left,right) in enumerate(pairs):
  for attempt in (1,2):
    try:
      payload={"model":model,"provider":{"order":["DeepSeek"],"allow_fallbacks":False,"require_parameters":True},"reasoning":{"effort":"medium"},"messages":[{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"left":events[left],"right":events[right]},ensure_ascii=False)}],"response_format":{"type":"json_schema","json_schema":{"name":"ubik_pair_judgment","strict":True,"schema":{"type":"object","additionalProperties":False,"required":["decision","direction","reason","detail_conflicts"],"properties":{"decision":{"type":"string","enum":["equivalent","distinct","uncertain","part_of"]},"direction":{"type":["string","null"],"enum":["left_part_of_right","right_part_of_left",None]},"reason":{"type":"string"},"detail_conflicts":{"type":"array","items":{"type":"string"}}}}}},"max_tokens":3000}
      req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["UBIK_LLM_API_KEY"],"Content-Type":"application/json"})
      with urllib.request.urlopen(req,timeout=240) as resp: raw=json.load(resp)
      usage=raw.get("usage",{})
      out["usage"].append({"pair":[left,right],"attempt":attempt,"model":raw.get("model"),"provider":raw.get("provider"),"usage":usage,"reasoning_tokens":usage.get("completion_tokens_details",{}).get("reasoning_tokens"),"cost_usd":usage.get("cost")})
      if raw.get("model")!=model:raise RuntimeError("Model identity mismatch; abort")
      if raw.get("provider") and raw["provider"].lower()!="deepseek":raise RuntimeError("Provider identity mismatch; abort")
      answer=json.loads(raw["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```").strip())
      if answer.get("decision") not in ("equivalent","distinct","uncertain","part_of"):raise ValueError("invalid decision")
      if answer["decision"]=="part_of" and answer.get("direction") not in ("left_part_of_right","right_part_of_left"):raise ValueError("invalid direction")
      if not isinstance(answer.get("detail_conflicts"),list):raise ValueError("invalid detail_conflicts")
      if not isinstance(answer.get("reason"),str):raise ValueError("invalid reason")
      out["judgments"].append({"left":left,"right":right,"similarity":baseline["judgments"][idx]["similarity"],"result":answer})
      break
    except (ValueError,KeyError,TypeError,IndexError) as exc:
      out["errors"].append({"pair":[left,right],"attempt":attempt,"type":"invalid_response","error":str(exc)[:200]})
      if attempt==2:
        out["invalid_after_retry"].append([left,right])
        out["judgments"].append({"left":left,"right":right,"similarity":baseline["judgments"][idx]["similarity"],"result":{"decision":"uncertain","direction":None,"reason":"invalid_after_retry","detail_conflicts":[],"invalid_after_retry":True}})
    except Exception as exc:
      out["errors"].append({"pair":[left,right],"attempt":attempt,"type":"api_or_transport","error":str(exc)[:200]})
      save();raise
    finally:save()
  if len(out["invalid_after_retry"])>=7:
    out["status"]="partial_invalid_threshold";save();break
out["complete_pairs"]=len(out["judgments"])
out["total_cost_usd"]=sum(x["cost_usd"] for x in out["usage"] if isinstance(x.get("cost_usd"),(float,int)))
out["cost_complete"]=all(isinstance(x.get("cost_usd"),(float,int)) for x in out["usage"])
out["total_pipeline_cost_usd"]=0.149988+out["total_cost_usd"]
out["reasoning_tokens_total"]=sum(x["reasoning_tokens"] for x in out["usage"] if isinstance(x.get("reasoning_tokens"),int))
out["reasoning_usage_complete"]=all(isinstance(x.get("reasoning_tokens"),int) for x in out["usage"])
out["within_cost_ceiling"]=out["cost_complete"] and out["total_pipeline_cost_usd"]<=0.671708
if len(out["judgments"])!=131 or len(out["invalid_after_retry"])>=7:
  out["status"]="partial";save();raise SystemExit("Incomplete/partial test; no promotion")
scores={(j["left"],j["right"]):j["similarity"] for j in baseline["judgments"]}
assembly=cautious_groups(events,out["judgments"],scores)
groups=assembly["groups"];lookup={e:"card:"+g[0] for g in groups for e in g}
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
out["assembly"]=assembly
out["relations"]=relations
out["quarantined_relations"]=rejected
out["composition"]=compose_connected_v5(cards,relations,conflicts=rejected)
out["disagreements"]=[{"left":j["left"],"right":j["right"],"sonnet":b["result"],"deepseek":j["result"]} for j,b in zip(out["judgments"],baseline["judgments"]) if (j["result"]["decision"],j["result"].get("direction"))!=(b["result"]["decision"],b["result"].get("direction"))]
out["status"]="completed_unadjudicated"
save()
print(json.dumps({"status":out["status"],"disagreements":len(out["disagreements"]),"cost":out["total_pipeline_cost_usd"],"invalid":len(out["invalid_after_retry"]),"cards":len(cards),"incidents":len(out["composition"]["incidents"])}))
