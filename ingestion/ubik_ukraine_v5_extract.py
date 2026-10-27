"""Ukraine v5 controlled Sonnet extraction, one independent source per call."""
import json,os,urllib.request
from pathlib import Path
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL,verify_response,verify_records
from ingestion.ubik_v5_extraction_validator import validate_extraction
ROOT=Path("data/ukraine-v5")
PROMPT="""Extract ONE source independently from its supplied titles and summaries, never pretend to have original articles. Return JSON only: events[] and assignments[]. Each event requires id, event_nature (container|fact), text_role (narrated|referenced), actor, action, object, actuality, event_time, evidence, container_name, context_signal, event_part_of[]. Each event_part_of item has event_id and nonempty evidence. Only grounded directed component-of links, not thematic proximity. assignments[] must cover every news key exactly once, with news_key, primary_event_id, reacts_to:[{event_id}], mentions:[event_id], context_only. Distinguish the executive order waiving sanctions from any separate diesel agreement. Reactions target the actual referenced act, not generic related news. Distinguish ceasefires and attacks. Do not use knowledge of other sources. Never invent facts, evidence, origins, or relations. Output only valid JSON."""
def main():
 if os.getenv("UBIK_LLM_MODEL")!=EXPECTED_MODEL:raise RuntimeError("Explicit Sonnet model required")
 data=json.loads((ROOT/"v4-sonnet55.json").read_text())
 if data["model"]!=EXPECTED_MODEL:raise RuntimeError("Baseline model mismatch")
 out={"model":EXPECTED_MODEL,"input_kind":"frozen_v4_titles_and_summaries","sources":[],"usage":[],"errors":[]}
 ROOT.mkdir(parents=True,exist_ok=True)
 def save():(ROOT/"v5-extraction.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
 for source in data["sources"]:
  payload={"source_id":source["source_id"],"news":source["news"]}
  try:
   req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps({"model":EXPECTED_MODEL,"messages":[{"role":"system","content":PROMPT},
     {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
     "response_format":{"type":"json_object"},"max_tokens":6500}).encode(),
    headers={"Authorization":"Bearer "+os.environ["UBIK_LLM_API_KEY"],"Content-Type":"application/json"})
   with urllib.request.urlopen(req,timeout=240) as response:raw=json.load(response)
   record=verify_response(raw,requested_model=EXPECTED_MODEL,stage="extract",source_id=source["source_id"])
   answer=json.loads(raw["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```").strip())
   try:validate_extraction(answer,payload)
   except Exception:
    out.setdefault('rejected_responses',[]).append({'source_id':source['source_id'],'answer':answer,'model_audit':record})
    raise
   out["sources"].append({"source_id":source["source_id"],"news":source["news"],"answer":answer})
   out["usage"].append(record)
  except Exception as exc:
   out["errors"].append({"source_id":source["source_id"],"error":str(exc)[:500]})
   save()
   raise
  save()
 out["cost_audit"]=verify_records(out["usage"])
 if len(out["sources"])!=len(data["sources"]):raise RuntimeError("Incomplete extraction")
 save()
 print(json.dumps({"sources":len(out["sources"]),"model":EXPECTED_MODEL,"cost":out["cost_audit"]}))
if __name__=="__main__":main()
