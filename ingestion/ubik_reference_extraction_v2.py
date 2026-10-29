"""Second independent extraction: reference identity precision, frozen 24 news."""
import json, os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

ROOT=Path("data/taxonomy-pilot")
old=json.loads((ROOT/"fact-reference-pilot.json").read_text())
assert len(old["items"])==24 and not old["errors"]
gold={
"A1":["3:n1"],"A2":["3:n29","3:n33"],"A3":["3:n18"],"A4":["3:n13"],"A5":["3:n30"],"A6":["3:n2"],
"B1":["3:n0","3:n15","3:n16","3:n31"],"B2":["3:n32","3:n34"],
"C1":["3:n11"],"C2":["3:n12"],"C3":["3:n14"],"C4":["3:n20"],
"D1":["3:n10"],"D2":["3:n27"],
"topic_only":["3:n22","3:n23","3:n24","3:n26","3:n28"]
}
assert len({n for keys in gold.values() for n in keys})==24
SYSTEM="""You are an evidence-grounded extractor of individual factual news. Process ONE news item IN ISOLATION. You never see other news. Return one JSON object with keys fact, references, uncertainties.
fact: {type, actor, action, object, recipient, time, place, identifiers, actuality, evidence}.
references: list of {type, actor, action, object, recipient, time, place, identifiers, actuality, relation, evidence, missing_fields}.
For EACH reference, fill the four identity-bearing dimensions:
(1) WHO carried out the REFERENCED act, not the speaker commenting on it; use null when absent;
(2) EXACT DISTINCTIVE OBJECT of the referenced act, retaining constraints and distinctions (diesel sanctions linked to a supply agreement vs a NEW sanctions/tariffs package); do not generalize away distinguishing details;
(3) WHEN, including relative chronology (e.g. one week earlier), but NEVER invent dates;
(4) ACTUALITY: occurred | announced | proposed | conditional | hypothetical | disputed | unknown. An announcement of an agreement is NOT proof the agreement occurred.
Only extract an independently identifiable prior or concurrent action, event, proposal, statement, or decision. Do NOT extract hypothetical consequences, broad background topics, generic ongoing war, or speculation as references. If a mentioned claim is unverified, distinguish reported allegation from established occurrence. If no concrete reference is identifiable, return [].
Every reference must have a short literal supporting phrase from title or summary in evidence. Do not fabricate exact quotes, legal identifiers, dates, actors, or source URLs. Unknown fields must be null. Preserve actor distinctions between governments, leaders, and individual envoys. Relation is one of criticizes, supports, responds_to, reports_on, precedes, follows, mentions, other; chronology is not causality. Return valid JSON only."""
output={"experiment":"reference_extraction_v2","model":os.environ.get("UBIK_LLM_MODEL"),"source_run":40140189703,"gold_reference":gold,"gold_note":"Evaluation only; never sent to model","items":[],"errors":[]}
for item in old["items"]:
 payload={"title":item["title"],"summary":item["summary"]}
 try:
  answer,meta=request_analysis([{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
  if not isinstance(answer,dict) or not isinstance(answer.get("fact"),dict) or not isinstance(answer.get("references"),list):raise ValueError("Invalid extraction structure")
  output["items"].append({"key":item["key"],"source_id":item["source_id"],"title":item["title"],"summary":item["summary"],"old_extraction":item["extraction"],"new_extraction":answer})
 except Exception as exc:output["errors"].append({"key":item["key"],"error":str(exc)[:250]})
 ROOT.joinpath("reference-extraction-v2.json").write_text(json.dumps(output,ensure_ascii=False,indent=2))
print(json.dumps({"processed":len(output["items"]),"errors":len(output["errors"]),"references_old":sum(len(i["old_extraction"]["references"]) for i in output["items"]),"references_new":sum(len(i["new_extraction"]["references"]) for i in output["items"]),"gold_cards":14,"gold_matrices":4},ensure_ascii=False))
