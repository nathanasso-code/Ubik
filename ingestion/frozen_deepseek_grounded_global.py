"""Source-grounded fundamental-news extraction and global card matching experiment."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

EXTRACT="""Read only the MAIN editorial body of this one source. Identify each DISTINCT, FUNDAMENTAL news development. A development is a meaningful action, decision, discovery or outcome that merits its own news summary, not a minor detail, statistic, incidental quote, sidebar or related link. Do not split details or immediate consequences of one event into separate news. Several truly independent developments are allowed. For each return a factual concise DISPLAY-READY title and 1-3 sentence summary, and 1-3 SHORT VERBATIM contiguous excerpts copied exactly from article_body. Do not paraphrase quotations or fabricate text. If text is only a video stub, judge whether its written description still documents a concrete news event. Return JSON {"source_id":"same ID","news":[{"title":"...","summary":"...","quotes":["exact substring"]}],"quality":"substantive|insufficient"}."""
GROUP="""You receive news extracted independently from original sources. Cluster by SAME SPECIFIC concrete news development, not broad subject or shared protagonist. Each distinct material divergence gets a separate card; minor details, reaction quotes or figures of the SAME development do not. An individual source can belong to several cards. Preserve EVERY input news id exactly once in groups, including singleton news. Write a factual short DISPLAY-READY title and summary for each group, grounded in its member news only. Never attribute to a source a fact not in that source. Return JSON {"cards":[{"news_ids":["n0","n3"],"title":"...","summary":"1-3 sentences"}]}. No omissions or duplicates."""
def ask(prompt,payload,out):
 result,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
 out["calls"]+=1;usage_add(out["usage"],usage)
 if not isinstance(result,dict):raise ValueError("non-object response")
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument("graph",type=Path);p.add_argument("metadata",type=Path);p.add_argument("texts",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 titles={s["id"]:s["title"] for s in graph["sources"]}
 bodies={s["source_id"]:s["text"] for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
 contexts=[{"source_ids":[s for s in c["source_ids"] if s in bodies]} for c in meta["reviews"] if sum(s in bodies for s in c["source_ids"])>=2]
 out={"phase":"grounded_global_cards","sources":{},"contexts":[],"errors":[],"calls":0,"usage":{}}
 ids=list(dict.fromkeys(s for c in contexts for s in c["source_ids"]))
 for sid in ids:
  body=bodies[sid][:7000]
  try:
   r=ask(EXTRACT,{"source_id":sid,"title":titles[sid],"article_body":body},out)
   if r.get("source_id")!=sid or not isinstance(r.get("news"),list):raise ValueError("invalid extraction")
   news=[]
   for n in r["news"]:
    if not isinstance(n,dict) or not all(isinstance(n.get(k),str) and n[k].strip() for k in ("title","summary")):continue
    quotes=n.get("quotes",[])
    if not isinstance(quotes,list):quotes=[]
    verified=[{"text":q,"start":body.find(q),"end":body.find(q)+len(q)} for q in quotes if isinstance(q,str) and q and q in body]
    if not verified:
     out["errors"].append({"source_id":sid,"title":n["title"],"error":"No verified literal evidence; news excluded"});continue
    news.append({"title":n["title"],"summary":n["summary"],"evidence":verified})
   out["sources"][sid]={"title":titles[sid],"quality":r.get("quality"),"news":news,"raw_news_count":len(r["news"])}
  except Exception as exc:out["errors"].append({"source_id":sid,"error":str(exc)[:250]})
  write(a.output,out)
 for ci,ctx in enumerate(contexts):
  items=[{"id":"n"+str(k),"source_id":sid,"title":n["title"],"summary":n["summary"]} for k,(sid,n) in enumerate((sid,n) for sid in ctx["source_ids"] for n in out["sources"].get(sid,{}).get("news",[]))]
  result={"context":ci,"source_ids":ctx["source_ids"],"news":items,"cards":[],"errors":[]}
  if not items:out["contexts"].append(result);write(a.output,out);continue
  try:
   r=ask(GROUP,{"news":items},out);lookup={n["id"]:n for n in items};used=set()
   for card in r.get("cards",[]):
    members=card.get("news_ids",[]) if isinstance(card,dict) else []
    if not isinstance(members,list) or not members or any(m not in lookup or m in used for m in members) or len(set(members))!=len(members):continue
    used.update(members);source_ids=list(dict.fromkeys(lookup[m]["source_id"] for m in members))
    result["cards"].append({"id":"c"+str(len(result["cards"])),"title":card.get("title",""),"summary":card.get("summary",""),"news_ids":members,"source_ids":source_ids,"evidence":[{"source_id":lookup[m]["source_id"],"news_id":m,"source_summary":lookup[m]["summary"],"passages":out["sources"][lookup[m]["source_id"]]["news"][int(m[1:]) if False else 0]["evidence"]} for m in []]})
   for n in items:
    if n["id"] not in used:
     result["errors"].append({"news_id":n["id"],"error":"unassigned; preserved as singleton"})
     result["cards"].append({"id":"c"+str(len(result["cards"])),"title":n["title"],"summary":n["summary"],"news_ids":[n["id"]],"source_ids":[n["source_id"]]})
   for card in result["cards"]:
    card["evidence"]=[]
    for nid in card["news_ids"]:
     item=lookup[nid];sid=item["source_id"]
     original=next((n for n in out["sources"][sid]["news"] if n["title"]==item["title"] and n["summary"]==item["summary"]),None)
     if original:card["evidence"].append({"source_id":sid,"news_id":nid,"source_summary":item["summary"],"passages":original["evidence"]})
  except Exception as exc:
   result["errors"].append({"error":str(exc)[:250]})
   for n in items:result["cards"].append({"id":"c"+str(len(result["cards"])),"title":n["title"],"summary":n["summary"],"news_ids":[n["id"]],"source_ids":[n["source_id"]]})
  out["contexts"].append(result);write(a.output,out)
 out["summary"]={"sources_expected":len(ids),"sources_extracted":len(out["sources"]),"news":sum(len(s["news"]) for s in out["sources"].values()),"cards":sum(len(c["cards"]) for c in out["contexts"]),"sources_in_cards":len(set(s for c in out["contexts"] for card in c["cards"] for s in card["source_ids"])),"errors":len(out["errors"])+sum(len(c["errors"]) for c in out["contexts"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
