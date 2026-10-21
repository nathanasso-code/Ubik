"""Differential cards with explicit editorial autonomy and exhaustive identity accounting.
Reuses 296 frozen fine identities; one composition and one audit call per context.
"""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add
COMPOSE="""You are an editor organizing fine-grained sourced facts into PERTINENT DISTINCT news cards. A card is justified by an autonomous substantial news development, NOT by every different detail. Sources can appear on multiple cards when their specific facts support distinct developments. Combine compatible facts even when from articles with different central subjects. Avoid forcing unrelated events into one card. Avoid separate cards for technology, method, background or reaction when these are naturally complementary details of the same development. For each card list the supporting claim IDs and articulate its unique substantive development. Prefer complete, nonredundant 2-3 sentence summaries; cite no facts not supported by listed claims. Return JSON {"cards":[{"title":"...","summary":"...","distinctive_development":"...","claim_ids":["c0"]}]}."""
AUDIT="""You are an independent evidence editor auditing proposed news cards against ALL supplied sourced factual identities. First detect overly granular cards that merely split complementary details of the same development; merge them when a coherent summary preserves their information. Next detect improper merges of unrelated developments and split where necessary. Preserve distinct substantive stories. Finally ACCOUNT FOR EVERY input claim ID exactly once: assigned to ONE card as distinctive/supporting evidence, redundant with an already represented claim, or secondary detail that does not warrant a card. If a substantial fact is missing, add it to an existing appropriate card or create a genuinely autonomous card. Multiple source IDs may support each card and sources can recur across cards. Never invent. Output JSON {"cards":[{"title":"...","summary":"2-3 factual sentences","distinctive_development":"specific autonomous development","claim_ids":["c0"]}],"redundant_claim_ids":["c1"],"secondary_claim_ids":["c2"],"important_uncovered_claim_ids":["c3"],"audit_notes":["..."]}. IDs in the three non-card categories must not overlap card claim IDs. Every ID must appear in exactly one category. If uncertain about a claim's relevance, classify it important_uncovered rather than silently omit. Limit audit_notes to key material decisions."""
def main():
 p=argparse.ArgumentParser();p.add_argument("identity_result",type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 data=json.loads(a.identity_result.read_text());out={"variant":"fine_identity_autonomy_coverage_audit","source_analysis_reused":True,"contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Reuses unverified frozen fine identities, not full articles.","Editorial audit is LLM-based; factual fidelity still requires checking original texts."]}
 endpoint=os.environ["UBIK_LLM_ENDPOINT"];model=os.environ["UBIK_LLM_MODEL"];key=os.environ["UBIK_LLM_API_KEY"]
 def ask(prompt,payload):
  response,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=150)
  out["calls"]+=1;usage_add(out["usage"],usage);return response
 for ci,context in enumerate(data["contexts"]):
  claims=[]
  for sid in context["source_ids"]:
   for j,x in enumerate(data["sources"].get(sid,{}).get("identities",[])):
    if isinstance(x,dict) and isinstance(x.get("text"),str):
     claims.append({"id":"c"+str(len(claims)),"source_id":sid,"identity_index":j,"text":x["text"]})
  valid={x["id"]:x for x in claims}
  item={"tag":context.get("tag"),"source_ids":context["source_ids"],"claims":claims,"cards":[],"redundant_claim_ids":[],"secondary_claim_ids":[],"important_uncovered_claim_ids":[],"unaccounted_claim_ids":[],"invalid_cards":[],"audit_notes":[],"raw_composition_cards":[]}
  try:
   # All claims included: no 160-claim truncation.
   first=ask(COMPOSE,{"context":context.get("tag"),"claims":claims})
   item["raw_composition_cards"]=first.get("cards",[])
   second=ask(AUDIT,{"context":context.get("tag"),"claims":claims,"proposed_cards":item["raw_composition_cards"]})
   used=set()
   for card in second.get("cards",[]):
    refs=card.get("claim_ids",[])
    if not isinstance(refs,list) or not refs or len(set(refs))!=len(refs) or not set(refs)<=valid.keys() or used.intersection(refs) or not all(isinstance(card.get(k),str) and card[k].strip() for k in ("title","summary","distinctive_development")):
     item["invalid_cards"].append(card);continue
    used.update(refs)
    item["cards"].append({"title":card["title"],"summary":card["summary"],"distinctive_development":card["distinctive_development"],"claim_ids":refs,"source_ids":list(dict.fromkeys(valid[r]["source_id"] for r in refs))})
   for category in ("redundant_claim_ids","secondary_claim_ids","important_uncovered_claim_ids"):
    values=second.get(category,[])
    if not isinstance(values,list):values=[]
    item[category]=[v for v in values if v in valid and v not in used]
    used.update(item[category])
   item["unaccounted_claim_ids"]=sorted(set(valid)-used,key=lambda s:int(s[1:]))
   item["audit_notes"]=second.get("audit_notes",[])
  except Exception as exc:
   out["errors"].append({"context":ci,"error":str(exc)[:250]})
   item["unaccounted_claim_ids"]=list(valid)
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"contexts":len(out["contexts"]),"sources":len(data["sources"]),"claims":sum(len(c["claims"]) for c in out["contexts"]),"cards":sum(len(c["cards"]) for c in out["contexts"]),"multi_source_cards":sum(sum(len(x["source_ids"])>1 for x in c["cards"]) for c in out["contexts"]),"redundant":sum(len(c["redundant_claim_ids"]) for c in out["contexts"]),"secondary":sum(len(c["secondary_claim_ids"]) for c in out["contexts"]),"important_uncovered":sum(len(c["important_uncovered_claim_ids"]) for c in out["contexts"]),"unaccounted":sum(len(c["unaccounted_claim_ids"]) for c in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
