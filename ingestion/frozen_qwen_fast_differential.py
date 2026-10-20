"""Fast frozen comparison: parallel source extraction, one grouping+synthesis call per context."""
import argparse,concurrent.futures,json,os,threading
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add
from ingestion.frozen_qwen_differential_cards import EXTRACT

GROUP_AND_SUMMARIZE="""Compare the MAIN news developments from sources in this context. Group developments only when they describe the same specific news event; details may differ. Separate meaningfully different decisions, reactions, actions, or outcomes even when they share context. A source may support several groups through different developments. Every development must be assigned exactly once, including standalone groups. For EACH group, provide a short headline and a 2-3 sentence synthesis emphasizing what distinguishes it from other groups; use shared background only when needed. Use only facts in the assigned developments; never invent agreement or differences. Return JSON {"groups":[{"title":"distinctive specific headline","summary":"2-3 factual sentences","members":[{"source_id":"...","development_index":0}]}]}. Do not invent IDs or indices."""

def main():
 p=argparse.ArgumentParser()
 for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
 p.add_argument("--output",type=Path,required=True)
 p.add_argument("--workers",type=int,default=4)
 a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 byid={x["id"]:x for x in graph["sources"]}
 body={x["source_id"]:x["text"] for x in texts["sources"] if x.get("status")=="extracted_unverified" and len(x.get("text",""))>=800}
 cases=[c for c in meta["reviews"] if sum(s in body for s in c["source_ids"])>=2]
 ids=list(dict.fromkeys(s for c in cases for s in c["source_ids"] if s in body))
 out={"variant":"fast_differential","sources":{},"contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Frozen corpus, not ground truth.","Article bodies truncated at 7000 characters.","Parallel extraction may be rate-limited by provider."]}
 endpoint=os.environ["UBIK_LLM_ENDPOINT"];model=os.environ["UBIK_LLM_MODEL"];key=os.environ["UBIK_LLM_API_KEY"]
 lock=threading.Lock()
 def ask(prompt,payload):
  answer,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
  with lock:
   out["calls"]+=1;usage_add(out["usage"],usage)
  return answer
 def extract(sid):
  for attempt in range(3):
   try:
    ans=ask(EXTRACT,{"source_id":sid,"title":byid[sid]["title"],"article_body":body[sid][:7000]})
    ds=ans.get("developments")
    if ans.get("source_id")!=sid or not isinstance(ds,list) or any(not isinstance(d,dict) or not all(isinstance(d.get(k),str) for k in ("title","summary","evidence")) for d in ds):raise ValueError("invalid extraction schema")
    return sid,ans,None
   except Exception as e:
    if attempt==2:return sid,None,str(e)[:200]
 with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(6,a.workers))) as pool:
  for sid,ans,err in pool.map(extract,ids):
   if ans:out["sources"][sid]=ans
   else:out["errors"].append({"stage":"extraction","source_id":sid,"error":err})
   write(a.output,out)
 for ci,c in enumerate(cases):
  members=[s for s in c["source_ids"] if s in out["sources"]]
  developments=[{"source_id":sid,"development_index":j,"title":d["title"],"summary":d["summary"]} for sid in members for j,d in enumerate(out["sources"][sid]["developments"])]
  valid={(x["source_id"],x["development_index"]) for x in developments}
  context={"source_ids":members,"groups":[],"invalid":[],"unassigned":[]}
  assigned=set()
  try:
   response=ask(GROUP_AND_SUMMARIZE,{"developments":developments})
   if not isinstance(response.get("groups"),list):raise ValueError("missing groups")
   for g in response["groups"]:
    raw=g.get("members",[])
    pairs=[(m.get("source_id"),m.get("development_index")) for m in raw if isinstance(m,dict)]
    if not pairs or len(pairs)!=len(raw) or len(set(pairs))!=len(pairs) or not set(pairs)<=valid or set(pairs)&assigned or len({s for s,j in pairs})!=len(pairs) or not isinstance(g.get("title"),str) or not isinstance(g.get("summary"),str):
     context["invalid"].append(g);continue
    assigned.update(pairs)
    context["groups"].append({"title":g["title"],"summary":g["summary"],"members":raw,"source_ids":[s for s,j in pairs],"type":"card" if len(pairs)>1 else "standalone"})
  except Exception as e:out["errors"].append({"stage":"context","context":ci,"error":str(e)[:200]})
  for sid,j in sorted(valid-assigned):
   d=out["sources"][sid]["developments"][j]
   context["unassigned"].append({"source_id":sid,"development_index":j})
   context["groups"].append({"title":d["title"],"summary":d["summary"],"members":[{"source_id":sid,"development_index":j}],"source_ids":[sid],"type":"standalone","recovered":True})
  out["contexts"].append(context);write(a.output,out)
 out["summary"]={"eligible_sources":len(ids),"extracted_sources":len(out["sources"]),"contexts":len(out["contexts"]),"cards":sum(sum(g["type"]=="card" for g in c["groups"]) for c in out["contexts"]),"standalones":sum(sum(g["type"]=="standalone" for g in c["groups"]) for c in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
