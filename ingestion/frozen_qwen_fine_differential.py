"""Differential card composition from frozen fine-grained Qwen identity analysis.
No re-extraction: 8 context calls, baseline cards retained for direct comparison.
"""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

PROMPT="""You are organizing a news context into DISTINCT informative cards, using already-extracted factual claims.
Each claim has an ID and its supporting source. Some claims overlap.
Create a SMALL number of coherent cards, each telling a DIFFERENT meaningful part of the story.
Choose each card's specific focus from claims that distinguish it from OTHER cards, not from generic shared background.
You MAY combine sources with different overall articles if their claims jointly support the card's focus.
A source may support multiple cards, but cite it only for claims relevant to that card.
Use overlapping claims as brief context, never as a reason to repeat the same synthesis in multiple cards.
Do not create a new card for a trivial detail. Do not combine unrelated events just because they share a topic.
Every factual claim in a card must be supported by listed claim IDs. Do not infer new facts.
Keep important claims that do not fit a card as uncovered; never force them into unrelated cards.
Return JSON {"cards":[{"title":"specific distinctive headline","summary":"2-3 factual sentences emphasizing the distinctive contribution","claim_ids":["c0","c1"]}],"uncovered_claim_ids":["c2"]}.
Use each claim ID at most once as a card's DISTINCTIVE evidence; shared background may be omitted.
If there are many claims, prioritize important developments and avoid long outputs."""
def main():
 p=argparse.ArgumentParser();p.add_argument("identity_result",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 data=json.loads(a.identity_result.read_text())
 out={"variant":"differential_from_fine_identity","source_analysis_reused":True,"contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Claims inherited from earlier unverified LLM extraction.","No original article text in composition prompt.","Context input limited to 160 claims."]}
 endpoint=os.environ["UBIK_LLM_ENDPOINT"];model=os.environ["UBIK_LLM_MODEL"];key=os.environ["UBIK_LLM_API_KEY"]
 for ci,context in enumerate(data["contexts"]):
  ids=context["source_ids"];claims=[]
  for sid in ids:
   for j,x in enumerate(data["sources"].get(sid,{}).get("identities",[])):
    if isinstance(x,dict) and isinstance(x.get("text"),str):
     claims.append({"id":"c"+str(len(claims)),"source_id":sid,"identity_index":j,"text":x["text"]})
  claims=claims[:160]
  valid={x["id"]:x for x in claims}
  item={"tag":context.get("tag"),"source_ids":ids,"baseline_identity_cards":context.get("cards",[]),"baseline_identity_card_count":len(context.get("cards",[])),"claims":claims,"cards":[],"uncovered_claim_ids":[],"invalid":[]}
  try:
   response,usage=request_analysis([{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"context":context.get("tag"),"claims":claims},ensure_ascii=False)}],endpoint,model,key,timeout=120)
   out["calls"]+=1;usage_add(out["usage"],usage)
   assigned=set()
   for card in response.get("cards",[]):
    refs=card.get("claim_ids",[])
    if not isinstance(refs,list) or not refs or len(set(refs))!=len(refs) or not set(refs)<=valid.keys() or set(refs)&assigned or not isinstance(card.get("title"),str) or not isinstance(card.get("summary"),str):
     item["invalid"].append(card);continue
    assigned.update(refs)
    item["cards"].append({"title":card["title"],"summary":card["summary"],"claim_ids":refs,"source_ids":list(dict.fromkeys(valid[r]["source_id"] for r in refs)),"type":"multi_source" if len({valid[r]["source_id"] for r in refs})>1 else "single_source"})
   item["uncovered_claim_ids"]=sorted(set(valid)-assigned,key=lambda s:int(s[1:]))
  except Exception as e:
   out["errors"].append({"context":ci,"error":str(e)[:240]})
   item["uncovered_claim_ids"]=list(valid)
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"contexts":len(out["contexts"]),"input_sources":len(data["sources"]),"baseline_cards":sum(x["baseline_identity_card_count"] for x in out["contexts"]),"differential_cards":sum(len(x["cards"]) for x in out["contexts"]),"multi_source_cards":sum(sum(c["type"]=="multi_source" for c in x["cards"]) for x in out["contexts"]),"uncovered_claims":sum(len(x["uncovered_claim_ids"]) for x in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
