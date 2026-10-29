"""V4 frozen 24-news extraction. Grouped summaries only; no gold in model input."""
import json,os,re,sys,urllib.request,urllib.error,traceback
from pathlib import Path
from collections import defaultdict
from ingestion.ubik_json_response import parse_json_response
ROOT=Path("data/taxonomy-pilot")
SYSTEM="""You extract events and news relationships from titles and summaries of ONE source. Do not assume access to the original article. Do not compare sources.
First identify each news item's PRIMARY narrated event or claim (including a criticism, endorsement, position, or report).
Separately extract concrete REFERENCED events even if no news item narrates them as its main fact. For EACH news item explicitly ask: does this main fact react directly to a distinct concrete decision, agreement, attack, announcement or other identifiable event? If yes, record it in reacts_to, even if the event is only mentioned in this source. If it merely provides contextual background, record in mentions, not reacts_to. An event mentioned in a news item must NOT automatically become its matrix.
Events must have a concrete action, specific object and verbatim evidence. Do not invent actor when omitted; null is allowed. Exclude generic wars, processes, predictions and hypothetical consequences as referenced events. Keep distinct acts separate when their concrete objects or temporal relationships differ; do not collapse events merely because they share actors or broad topics. Use relative time when provided.
Each event: id E1..., event_role narrated|referenced, actor (short entity or null), action, object, time (string or null), actuality occurred|announced|proposed|conditional|disputed|unknown, evidence (verbatim excerpt from supplied title or summary), evidence_news_keys (news keys).
Each assignment: news_key, primary_event_id (E id or null), reacts_to (array of E ids), reacts_to_status linked|none|unidentifiable, reacts_to_explanation (string or null), mentions (array of E ids). Primary event is the news's own principal claim, NOT the policy or attack that its speaker comments on. reacts_to never contains primary_event_id. For unidentifiable use [] and explain; for none use [].
Return one JSON object with events and assignments. Cover every supplied news key exactly once. Do not use gold labels."""
SCHEMA={"type":"object","additionalProperties":False,"required":["events","assignments"],"properties":{
"events":{"type":"array","items":{"type":"object","additionalProperties":False,"required":["id","event_role","actor","action","object","time","actuality","evidence","evidence_news_keys"],"properties":{
"id":{"type":"string"},"event_role":{"type":"string","enum":["narrated","referenced"]},"actor":{"type":["string","null"]},"action":{"type":"string"},"object":{"type":"string"},"time":{"type":["string","null"]},"actuality":{"type":"string","enum":["occurred","announced","proposed","conditional","disputed","unknown"]},"evidence":{"type":"string"},"evidence_news_keys":{"type":"array","items":{"type":"string"}}}}},
"assignments":{"type":"array","items":{"type":"object","additionalProperties":False,"required":["news_key","primary_event_id","reacts_to","reacts_to_status","reacts_to_explanation","mentions"],"properties":{
"news_key":{"type":"string"},"primary_event_id":{"type":["string","null"]},"reacts_to":{"type":"array","items":{"type":"string"}},"reacts_to_status":{"type":"string","enum":["linked","none","unidentifiable"]},"reacts_to_explanation":{"type":["string","null"]},"mentions":{"type":"array","items":{"type":"string"}}}}}}}
def validate(ans,source,items):
 if not isinstance(ans,dict) or not isinstance(ans.get("events"),list) or not isinstance(ans.get("assignments"),list):raise ValueError("invalid root")
 keys={x["key"] for x in items}
 ids=set()
 for ev in ans["events"]:
  ident=ev.get("id")
  if not isinstance(ident,str) or not re.fullmatch(r"E[1-9][0-9]*",ident) or ident in ids:raise ValueError("invalid/duplicate event id")
  ids.add(ident)
  if ev.get("event_role") not in ("narrated","referenced"):raise ValueError("invalid event_role")
  if ev.get("actor") is not None and (not isinstance(ev["actor"],str) or len(ev["actor"])>65):raise ValueError("invalid actor")
  for field in ("action","object","evidence"):
   if not isinstance(ev.get(field),str) or not ev[field].strip():raise ValueError("empty "+field+" for "+ident)
  if ev.get("actuality") not in ("occurred","announced","proposed","conditional","disputed","unknown"):raise ValueError("invalid actuality")
  if not isinstance(ev.get("evidence_news_keys"),list) or not ev["evidence_news_keys"] or any(k not in keys for k in ev["evidence_news_keys"]):raise ValueError("invalid evidence keys")
  texts="\n".join((x.get("title","")+"\n"+x.get("summary","")) for x in items if x["key"] in ev["evidence_news_keys"])
  if ev["evidence"].strip().casefold() not in texts.casefold():raise ValueError("ungrounded evidence for "+ident)
 assignments=ans["assignments"]
 if len(assignments)!=len(keys) or {a.get("news_key") for a in assignments}!=keys:raise ValueError("missing/duplicate assignments")
 for a in assignments:
  p=a.get("primary_event_id")
  if p is not None and p not in ids:raise ValueError("missing primary event "+str(p))
  if a.get("reacts_to_status") not in ("linked","none","unidentifiable"):raise ValueError("missing reacts_to_status")
  for f in ("reacts_to","mentions"):
   if not isinstance(a.get(f),list) or any(i not in ids for i in a[f]):raise ValueError("invalid "+f)
  if p in a["reacts_to"]:raise ValueError("self reaction")
  if set(a["reacts_to"]) & set(a["mentions"]):raise ValueError("reaction also mentioned")
  if (a["reacts_to_status"]=="linked") != bool(a["reacts_to"]):raise ValueError("reaction status mismatch")
  if a["reacts_to_status"]=="unidentifiable" and not a.get("reacts_to_explanation"):raise ValueError("unidentifiable without explanation")
 return ans
def query(inp,model,key):
 payload={"model":model,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(inp,ensure_ascii=False)}],"response_format":{"type":"json_schema","json_schema":{"name":"ubik_v4","strict":True,"schema":SCHEMA}},"max_tokens":6500}
 # Sonnet 5.5 rejects temperature; no temperature parameter is sent to either model.
 req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
 try:
  with urllib.request.urlopen(req,timeout=210) as resp:body=json.loads(resp.read())
 except urllib.error.HTTPError as exc:
  raw=exc.read(8192).decode("utf-8","replace")
  try:
   err=json.loads(raw).get("error",{})
   msg=str(err.get("message",""))[:300] if isinstance(err,dict) else ""
  except Exception:msg=""
  raise RuntimeError("HTTP "+str(exc.code)+" "+msg) from None
 msg=body["choices"][0]["message"]
 content=msg.get("content")
 return parse_json_response(content),body.get("usage",{}),content
def main():
 source_data=json.loads((ROOT/"fact-reference-pilot.json").read_text())
 items=source_data["items"]
 assert len(items)==24
 by_source=defaultdict(list)
 for item in items:by_source[item["source_id"]].append(item)
 assert len(by_source)==9
 label=os.environ["UBIK_MODEL_LABEL"];model=os.environ["UBIK_LLM_MODEL"]
 out={"experiment":"v4_source_events","model":model,"input_mode":"summaries_not_full_text","gold_in_prompt":False,"sources":[],"errors":[],"expected_sources":9,"expected_news":24,"schema_version":4}
 output=ROOT/("v4-"+label+".json")
 for source,news in sorted(by_source.items()):
  inp={"source_id":source,"input_mode":"summaries","news":[{"key":i["key"],"title":i["title"],"summary":i["summary"]} for i in news]}
  try:
   ans,usage,content=query(inp,model,os.environ["UBIK_LLM_API_KEY"])
   validate(ans,source,news)
   out["sources"].append({"source_id":source,"news":inp["news"],"events":[{**ev,"qualified_id":source+":"+ev["id"]} for ev in ans["events"]],"assignments":ans["assignments"],"usage":usage})
  except Exception as exc:
   out["errors"].append({"source_id":source,"error_type":type(exc).__name__,"error":str(exc)[:350]})
  output.parent.mkdir(parents=True,exist_ok=True)
  output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"model":model,"sources":len(out["sources"]),"errors":out["errors"],"events":sum(len(s["events"]) for s in out["sources"]),"assignments":sum(len(s["assignments"]) for s in out["sources"])},ensure_ascii=False))
 if out["errors"] or len(out["sources"])!=9 or sum(len(s["assignments"]) for s in out["sources"])!=24:sys.exit(1)
if __name__=="__main__":main()
