import json, os, re
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

root=Path("data/taxonomy-pilot")
data=json.loads((root/"fewshot-results.json").read_text())
records=[r for r in data["arms"]["examples_4"]["records"] if r.get("status")=="ok" and r["news"].get("context")==3]
keywords=("sanction","diesel","ceasefire","cease-fire","truce","energy","zelensk","trump","sanzion","tregua")
selected=[r for r in records if any(w in (r["news"].get("title","")+" "+r["news"].get("summary","")).lower() for w in keywords)]
selected=selected[:24]
system="""You are a factual information extractor. Process ONE news item IN ISOLATION. Do not infer relationships to unseen news or form clusters. Return ONLY a JSON object:
{"fact":{"type":"decision|declaration|proposal|attack|agreement|event|other","actor":"","action":"","object":"","recipient":"","date":"","place":"","identifiers":[]},"references":[{"type":"","actor":"","action":"","object":"","recipient":"","date":"","place":"","identifiers":[],"relation":"criticizes|supports|responds_to|reports_on|consequence_of|mentions|other","explicit":true,"evidence":""}],"uncertainties":[]}
FACT is the primary reported occurrence. REFERENCES are distinct prior/concurrent acts, decisions, proposals or events explicitly mentioned or unambiguously described by the text, not broad topics. Extract references even if the source does not name their official title. Use null for unknown values. Do not invent dates, legal identifiers, recipients, or details. Preserve important specificity (diesel versus all energy sanctions; proposal versus agreed ceasefire). If there is no identifiable referenced act, return [].
"""
out={"experiment":"independent_fact_reference_extraction","sample_size":len(selected),"items":[],"errors":[]}
target=root/"fact-reference-pilot.json"
for r in selected:
 n=r["news"]
 payload={"title":n.get("title"),"summary":n.get("summary")}
 try:
  answer,meta=request_analysis([{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
  if not isinstance(answer,dict) or not isinstance(answer.get("fact"),dict) or not isinstance(answer.get("references"),list):raise ValueError("Invalid extraction structure")
  out["items"].append({"key":n["key"],"source_id":n.get("source_id"),"title":n.get("title"),"summary":n.get("summary"),"extraction":answer})
 except Exception as e:out["errors"].append({"key":n["key"],"error":str(e)[:250]})
 target.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({"selected":len(selected),"extracted":len(out["items"]),"errors":len(out["errors"])},ensure_ascii=False))
