"""Single-call per context: faithful summary, focus, distinctive contributions, differential cards."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add
SYSTEM="""Read ALL provided articles independently first. For each source provide a faithful 2-3 sentence summary, one precise central_focus, and up to THREE meaningful distinctive contributions (not generic background). Ignore sidebars, navigation, unrelated links, and non-article content. Mark insufficient texts.
Then compose a SMALL set of coherent news cards, each describing a DIFFERENT meaningful aspect of the context. Similar sources may be combined, but sources with different overall focuses may also be combined if their supported contributions tell one coherent development. Sources may appear in multiple cards. What distinguishes cards is their central information, NOT their source lists. Do not repeat the same development across cards or create a card for trivial details. Keep important unmatched contributions in their source summaries. Every card must identify the exact source IDs that support its DISTINCTIVE facts. Never invent facts or claim that a source supports details it does not.
Return JSON {"sources":[{"source_id":"exact id","quality":"substantive|insufficient","summary":"...","central_focus":"...","distinctive_contributions":["..."]}],"cards":[{"title":"specific headline","summary":"2-3 factual sentences","source_ids":["exact id"],"distinctive_focus":"specific contribution not covered by other cards"}],"uncertainties":["..."]}. Return all supplied source IDs exactly once."""
def main():
 p=argparse.ArgumentParser()
 for x in ("graph","metadata","texts"):p.add_argument(x,type=Path)
 p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 byid={x["id"]:x for x in graph["sources"]}
 bodies={x["source_id"]:x["text"] for x in texts["sources"] if x.get("status")=="extracted_unverified" and len(x.get("text",""))>=800}
 cases=[c for c in meta["reviews"] if sum(s in bodies for s in c["source_ids"])>=2]
 out={"variant":"one_call_summary_focus_differential","contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Frozen unverified source texts.","Bodies truncated at 7000 characters.","Source support validated structurally, not factually."]}
 for i,c in enumerate(cases):
  ids=[s for s in c["source_ids"] if s in bodies]
  payload={"sources":[{"id":sid,"title":byid[sid]["title"],"article_body":bodies[sid][:7000]} for sid in ids]}
  item={"source_ids":ids,"sources":[],"cards":[],"invalid_cards":[],"missing_sources":[]}
  try:
   answer,usage=request_analysis([{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=120)
   out["calls"]+=1;usage_add(out["usage"],usage)
   seen=set()
   for s in answer.get("sources",[]):
    if not isinstance(s,dict) or s.get("source_id") not in ids or s["source_id"] in seen:continue
    seen.add(s["source_id"]);item["sources"].append(s)
   item["missing_sources"]=sorted(set(ids)-seen)
   for card in answer.get("cards",[]):
    refs=card.get("source_ids",[])
    if not isinstance(refs,list) or not refs or len(set(refs))!=len(refs) or not set(refs)<=seen or not all(isinstance(card.get(k),str) and card[k].strip() for k in ("title","summary","distinctive_focus")):
     item["invalid_cards"].append(card);continue
    item["cards"].append(card)
   item["uncertainties"]=answer.get("uncertainties",[])
  except Exception as e:out["errors"].append({"context":i,"error":str(e)[:250]})
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"contexts":len(out["contexts"]),"sources":sum(len(x["sources"]) for x in out["contexts"]),"cards":sum(len(x["cards"]) for x in out["contexts"]),"multi_source_cards":sum(sum(len(c["source_ids"])>1 for c in x["cards"]) for x in out["contexts"]),"missing_sources":sum(len(x["missing_sources"]) for x in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
