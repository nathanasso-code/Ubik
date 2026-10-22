"""Reconcile editorially redundant strict-clique cards without merging source cliques."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

PROMPT="""Compare these candidate news cards within ONE context. Merge cards only when they report the SAME concrete event/development (not merely same topic, country, or policy area). Preserve separate events and contradictory claims. Return JSON {"clusters":[{"card_ids":["c0","c2"],"title":"specific factual headline","summary":"2-4 factual sentences"}]}. Each card ID must appear exactly once. Singletons required for unique events. Never invent facts. The source groups of each card MUST remain separate; this is editorial reconciliation, not source grouping."""

def main():
 p=argparse.ArgumentParser();p.add_argument("strict",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 original=json.loads(a.strict.read_text())
 out={"phase":"editorial_reconciliation","parent_variant":original.get("variant"),"contexts":[],"errors":[],"calls":0,"usage":{}}
 for ctx in original["contexts"]:
  cards=ctx.get("cards",[])
  item={"context":ctx["context"],"input_cards":len(cards),"news_cards":[],"errors":[]}
  candidates=[{"id":"c"+str(i),"title":c["title"],"summary":c["summary"],"source_ids":c["source_ids"],"group_ids":c["group_ids"]} for i,c in enumerate(cards)]
  clusters=[]
  if len(candidates)>1:
   try:
    result,usage=request_analysis([{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"cards":candidates},ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
    out["calls"]+=1;usage_add(out["usage"],usage)
    if not isinstance(result,dict) or not isinstance(result.get("clusters"),list):raise ValueError("invalid clusters")
    used=set()
    for cluster in result["clusters"]:
     if not isinstance(cluster,dict):continue
     refs=cluster.get("card_ids",[])
     if not isinstance(refs,list) or not refs or len(refs)!=len(set(refs)) or any(ref not in {c["id"] for c in candidates} or ref in used for ref in refs):continue
     if not isinstance(cluster.get("title"),str) or not isinstance(cluster.get("summary"),str):continue
     used.update(refs);clusters.append(cluster)
   except Exception as exc:
    item["errors"].append(str(exc)[:250]);out["errors"].append({"context":ctx["context"],"error":str(exc)[:250]})
  used={ref for cl in clusters for ref in cl["card_ids"]}
  for c in candidates:
   if c["id"] not in used:clusters.append({"card_ids":[c["id"]],"title":c["title"],"summary":c["summary"]})
  for cl in clusters:
   members=[cards[int(cid[1:])] for cid in cl["card_ids"]]
   item["news_cards"].append({"title":cl["title"],"summary":cl["summary"],"original_card_ids":cl["card_ids"],"source_groups":[{"source_ids":m["source_ids"],"group_ids":m["group_ids"]} for m in members],"source_ids":list(dict.fromkeys(s for m in members for s in m["source_ids"]))})
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"input_cards":sum(x["input_cards"] for x in out["contexts"]),"news_cards":sum(len(x["news_cards"]) for x in out["contexts"]),"sources":len(set(s for x in out["contexts"] for c in x["news_cards"] for s in c["source_ids"])),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
