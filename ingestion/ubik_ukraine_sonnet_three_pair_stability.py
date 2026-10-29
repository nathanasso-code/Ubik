"""Preregistered original-Sonnet repeat of three concise-format disagreements."""
import json,os,urllib.request
from pathlib import Path
from ingestion.ubik_ukraine_v5_judge import PROMPT
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL,verify_response,verify_records
root=Path("data/ukraine-sonnet-stability");root.mkdir(parents=True,exist_ok=True)
ex=json.loads((root/"v5-extraction.json").read_text())
original=json.loads((root/"v5-judge.json").read_text())
concise=json.loads((root/"sonnet-concise-result.json").read_text())
pairs=[("S387:e2","S465:e2"),("S188:e2","S383:e2"),("S389:e4","S408:e7")]
events={s["source_id"]+":"+e["id"]:e for s in ex["sources"] for e in s["answer"]["events"]}
assert len(original["judgments"])==len(concise["judgments"])==131
base={(j["left"],j["right"]):j for j in original["judgments"]}
short={(j["left"],j["right"]):j for j in concise["judgments"]}
assert len(base)==len(short)==131
assert all(p in base and p in short for p in pairs)
assert [(base[p]["result"]["decision"],short[p]["result"]["decision"]) for p in pairs]==[("uncertain","distinct"),("equivalent","uncertain"),("uncertain","distinct")]
out={"model":EXPECTED_MODEL,"protocol":"docs/experiment-results/sonnet-concise-three-pair-stability-preregistered-2026-10-28.md","original_artifact":"12725256478","concise_artifact":"12777392635","judgments":[],"usage":[],"errors":[]}
def save():(root/"sonnet-three-pair-stability.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
save()
for left,right in pairs:
 try:
  payload={"model":EXPECTED_MODEL,"messages":[{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"left":events[left],"right":events[right]},ensure_ascii=False)}],"response_format":{"type":"json_object"},"max_tokens":3000}
  req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["UBIK_LLM_API_KEY"],"Content-Type":"application/json"})
  with urllib.request.urlopen(req,timeout=240) as response:raw=json.load(response)
  audit=verify_response(raw,stage="judge",pair=[left,right])
  out["usage"].append(audit)
  result=json.loads(raw["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```").strip())
  if result.get("decision") not in ("equivalent","distinct","uncertain","part_of"):raise ValueError("Invalid decision")
  if result["decision"]=="part_of" and result.get("direction") not in ("left_part_of_right","right_part_of_left"):raise ValueError("Invalid direction")
  if not isinstance(result.get("reason"),str) or not isinstance(result.get("detail_conflicts"),list):raise ValueError("Invalid result schema")
  out["judgments"].append({"left":left,"right":right,"original":base[(left,right)]["result"],"concise":short[(left,right)]["result"],"repeat":result,"same_as_original":result["decision"]==base[(left,right)]["result"]["decision"],"same_as_concise":result["decision"]==short[(left,right)]["result"]["decision"]})
 except Exception as exc:
  out["errors"].append({"pair":[left,right],"error":str(exc)[:500]})
  save();raise
 save()
out["cost_audit"]=verify_records(out["usage"])
out["status"]="complete" if len(out["judgments"])==3 and not out["errors"] and out["cost_audit"]["cost_complete"] else "incomplete"
save()
print(json.dumps({"status":out["status"],"cost":out["cost_audit"],"results":[{"pair":[j["left"],j["right"]],"original":j["original"]["decision"],"concise":j["concise"]["decision"],"repeat":j["repeat"]["decision"]} for j in out["judgments"]]}))
