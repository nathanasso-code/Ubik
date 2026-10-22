"""Simple source-to-news-card baseline: one canonical development = one card.

Uses the frozen headline/brief extraction. Processes sources incrementally;
an incoming development either matches an existing card or creates a new card.
"""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

PROMPT="""You maintain a catalog of DISTINCT concrete news developments, not general topics.
For each incoming source news item, decide whether it reports the SAME specific event
as an existing card, or a genuinely NEW event. Same broad subject is NOT sufficient.
Prefer precise event identity (actor, action, object, time, outcome). If matching,
preserve existing card identity, and update its already-public-facing title/summary
only if new supported information materially improves it. Never invent or attribute
the new detail to other sources. Return JSON:
{"decisions":[{"news_id":"n0","action":"match|new","card_id":"c0 or null",
"title":"final display-ready headline","summary":"final display-ready 1-3 sentence factual summary"}]}.
Every incoming news_id exactly once. Match only IDs present in existing cards.
No unrelated sidebar information. No fixed number of cards."""
def main():
 p=argparse.ArgumentParser();p.add_argument("extraction",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 ext=json.loads(a.extraction.read_text())
 out={"phase":"simple_incremental_news_cards","contexts":[],"errors":[],"calls":0,"usage":{}}
 for ci,ctx in enumerate(ext["contexts"]):
  cards=[];errors=[];seen_sources=set()
  for sid in ctx["source_ids"]:
   if sid in seen_sources:continue
   seen_sources.add(sid)
   news=ext["sources"].get(sid,{}).get("news",[])
   incoming=[{"news_id":"n"+str(k),"title":n["title"],"summary":n["summary"],"evidence":n.get("evidence","")} for k,n in enumerate(news)]
   if not incoming:continue
   catalog=[{"card_id":c["id"],"title":c["title"],"summary":c["summary"]} for c in cards]
   try:
    if not catalog:
     decisions=[{"news_id":n["news_id"],"action":"new","title":n["title"],"summary":n["summary"]} for n in incoming]
    else:
     response,usage=request_analysis([{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"existing_cards":catalog,"incoming_source_id":sid,"incoming_news":incoming},ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
     out["calls"]+=1;usage_add(out["usage"],usage)
     if not isinstance(response,dict) or not isinstance(response.get("decisions"),list):raise ValueError("invalid decisions")
     decisions=response["decisions"]
    index={n["news_id"]:n for n in incoming};processed=set()
    for d in decisions:
     if not isinstance(d,dict):continue
     nid=d.get("news_id")
     if nid not in index or nid in processed:continue
     action=d.get("action");target=next((c for c in cards if c["id"]==d.get("card_id")),None)
     if action=="match" and target is not None:
      target["source_ids"]=list(dict.fromkeys(target["source_ids"]+[sid]))
      target["evidence"].append({"source_id":sid,"news_id":nid,"original_title":index[nid]["title"],"original_summary":index[nid]["summary"],"excerpt":index[nid]["evidence"]})
      if isinstance(d.get("title"),str) and d["title"].strip():target["title"]=d["title"]
      if isinstance(d.get("summary"),str) and d["summary"].strip():target["summary"]=d["summary"]
     else:
      cards.append({"id":"c"+str(len(cards)),"title":d.get("title") or index[nid]["title"],"summary":d.get("summary") or index[nid]["summary"],"source_ids":[sid],"evidence":[{"source_id":sid,"news_id":nid,"original_title":index[nid]["title"],"original_summary":index[nid]["summary"],"excerpt":index[nid]["evidence"]}]})
     processed.add(nid)
    for nid,n in index.items():
     if nid not in processed:
      errors.append({"source_id":sid,"news_id":nid,"error":"model omitted decision; preserved as new card"})
      cards.append({"id":"c"+str(len(cards)),"title":n["title"],"summary":n["summary"],"source_ids":[sid],"evidence":[{"source_id":sid,"news_id":nid,"original_title":n["title"],"original_summary":n["summary"],"excerpt":n["evidence"]}]})
   except Exception as exc:
    errors.append({"source_id":sid,"error":str(exc)[:250]})
    for n in incoming:
     cards.append({"id":"c"+str(len(cards)),"title":n["title"],"summary":n["summary"],"source_ids":[sid],"evidence":[{"source_id":sid,"news_id":n["news_id"],"original_title":n["title"],"original_summary":n["summary"],"excerpt":n["evidence"]}]})
  out["contexts"].append({"context":ci,"source_ids":ctx["source_ids"],"cards":cards,"errors":errors})
  write(a.output,out)
 out["summary"]={"contexts":len(out["contexts"]),"cards":sum(len(c["cards"]) for c in out["contexts"]),"sources_in_cards":len(set(s for ctx in out["contexts"] for c in ctx["cards"] for s in c["source_ids"])),"errors":sum(len(ctx["errors"]) for ctx in out["contexts"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
