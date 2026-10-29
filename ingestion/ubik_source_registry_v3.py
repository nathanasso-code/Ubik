"""V3: per-source event registry, then attach each news to local event IDs.
Input is explicitly summaries, NOT recovered full articles. No gold labels in prompts.
"""
import json,os,re
from pathlib import Path
from collections import defaultdict
from ingestion.llm_semantic_adapter import request_analysis

ROOT=Path("data/taxonomy-pilot")
old=json.loads((ROOT/"fact-reference-pilot.json").read_text())
v2=json.loads((ROOT/"reference-extraction-v2.json").read_text())
assert len(old["items"])==len(v2["items"])==24
v2_by={i["key"]:i for i in v2["items"]}
by_source=defaultdict(list)
for item in old["items"]:by_source[item["source_id"]].append(item)
assert len(by_source)==9,[(k,len(v)) for k,v in by_source.items()]
GOLD={"3:n0":"B","3:n1":"A","3:n2":"A","3:n10":"D","3:n11":"C","3:n12":"C","3:n13":"A","3:n14":"C","3:n15":"B","3:n16":"B","3:n18":"A","3:n20":"C","3:n22":None,"3:n23":None,"3:n24":None,"3:n26":None,"3:n27":"D","3:n28":None,"3:n29":"A","3:n30":"AMBIGUOUS","3:n31":"B","3:n32":"B","3:n33":"A","3:n34":"B"}
assert set(GOLD)=={i["key"] for i in old["items"]}
SYSTEM="""You extract an article-local registry of concrete events, and attach news statements to those events.
You receive multiple news items derived from ONE source article, not full article text. Never assume unseen article content. Never compare with other source articles. Work ONLY with the supplied titles and summaries.
Return JSON with two keys: events and assignments.
events: list of {id,actor,action,object,time,actuality,evidence_news_keys,evidence,identifiers}
id must be E1, E2 etc, unique within this source. actor is a short named person or institution ONLY (<=65 chars), or null. action is short verb phrase. object is SPECIFIC (distinguish diesel trade agreement and lifting diesel sanctions from executive order suspending NEW sanctions and tariffs). time is exact or relative when stated, else null. actuality is occurred|announced|proposed|conditional|hypothetical|disputed|unknown. identifiers is a list of exact identifiers explicitly provided, never invented. evidence is an exact short quotation from provided text, or null. evidence_news_keys is a list of keys supporting this event.
Only record specific concrete decisions, agreements, attacks, announcements, proposals or events directly mentioned. Exclude generic topics, predicted consequences and hypothetical future developments.
assignments: one for EACH supplied news key, {news_key,primary_event_id,referent_event_ids,notes}.
primary_event_id is the event being reported as the main fact, or null if none. referent_event_ids are event IDs that the reported statement is ABOUT, not its hypothetical consequences; may include its primary event when news directly reports the underlying event. In particular, a reaction to an event should point to that event, not only to the reaction itself. If the relevant referent is absent from the supplied evidence, return [] rather than invent.
Do not output relation labels (criticizes, precedes etc). Use only event IDs from your events list. Do not create an event merely because a desired link is missing. Keep contradictory or disputed claims marked as such.
Return valid JSON only."""
def validate(ans,source,items):
 if not isinstance(ans,dict) or not isinstance(ans.get("events"),list) or not isinstance(ans.get("assignments"),list):raise ValueError("invalid top-level")
 ids=set()
 for ev in ans["events"]:
  if not isinstance(ev,dict) or not re.fullmatch(r"E[1-9][0-9]*",str(ev.get("id",""))):raise ValueError("invalid event id")
  if ev["id"] in ids:raise ValueError("duplicate event id")
  ids.add(ev["id"])
  if ev.get("actor") is not None and (not isinstance(ev["actor"],str) or len(ev["actor"])>65):raise ValueError("invalid actor length")
  if not isinstance(ev.get("object"),str) or not ev["object"].strip():raise ValueError("missing object")
  if ev.get("actuality") not in ("occurred","announced","proposed","conditional","hypothetical","disputed","unknown"):raise ValueError("invalid actuality")
 keys={i["key"] for i in items}
 if {a.get("news_key") for a in ans["assignments"]}!=keys or len(ans["assignments"])!=len(keys):raise ValueError("assignment coverage")
 for a in ans["assignments"]:
  refs=a.get("referent_event_ids")
  if not isinstance(refs,list):raise ValueError("invalid referent list")
  if a.get("primary_event_id") is not None and a["primary_event_id"] not in ids:raise ValueError("invalid primary link")
  if any(ref not in ids for ref in refs):raise ValueError("invalid referent link")
 return ans
def main():
 out={"experiment":"v3_two_level_source_context","input_mode":"grouped_summaries_not_full_text","source_full_text_count_verified":0,"model":os.environ["UBIK_LLM_MODEL"],"criteria":{"threshold_correct":17,"denominator":23,"excluded":["3:n30"],"no_regression_from_v2":True,"gold_used_in_model":False},"gold_matrix_expected":GOLD,"sources":[],"errors":[],"baseline":{"v1":old["items"],"v2":v2["items"]}}
 for source,items in sorted(by_source.items()):
  inp={"source_id":source,"input_mode":"summaries","news":[{"key":i["key"],"title":i["title"],"summary":i["summary"]} for i in items]}
  try:
   ans,meta=request_analysis([{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(inp,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
   validate(ans,source,items)
   out["sources"].append({"source_id":source,"news":inp["news"],"events":[{**e,"qualified_id":source+":"+e["id"]} for e in ans["events"]],"assignments":ans["assignments"]})
  except Exception as exc:out["errors"].append({"source_id":source,"error":str(exc)[:300]})
  (ROOT/("v3-"+os.environ["UBIK_MODEL_LABEL"]+".json")).write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(json.dumps({"model":out["model"],"sources":len(out["sources"]),"errors":out["errors"],"events":sum(len(s["events"]) for s in out["sources"]),"assignments":sum(len(s["assignments"]) for s in out["sources"]),"mode":"summaries_only","note":"Gold evaluation requires manual evidence audit; no fabricated correctness score"},ensure_ascii=False))
if __name__=="__main__":main()
