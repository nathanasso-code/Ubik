"""Frozen 39-source experiment: principal developments -> coherent cards -> differential summaries."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

EXTRACT="""Read this one news article. Identify only the MAIN news developments it actually reports. For each development, write a specific short headline and a faithful 1-2 sentence summary. One development may contain several related details: do not split details into separate developments. A decision and a distinct reaction to it are separate developments only if both are substantively reported. Ignore background, related links, navigation and unrelated headlines. Do not invent facts. Return JSON: {"source_id":"exact ID","developments":[{"title":"specific headline","summary":"1-2 sentences","evidence":"short exact quotation from article supporting this development"}]}. Return an empty list when there is no substantive article content."""
GROUP="""You receive the independently extracted MAIN developments of articles from one broad news context. Group developments, NOT whole articles, into cards. Put two developments in the same card only if they describe substantially the SAME specific news development, even if one gives extra details. If their central actions, decisions, reactions, actors or outcomes differ meaningfully, make separate cards. Shared context alone is never enough. A source can contribute to multiple cards, but only through its corresponding development. Include singleton developments as standalone sources, NOT multi-source cards. Each development must appear in exactly one group. Do not invent sources or indexes. Return JSON {"groups":[{"focus":"specific unique development headline","members":[{"source_id":"...","development_index":0}]}]}."""
SUMMARIZE="""Write a short factual synthesis for ONE card, using ONLY the supplied developments. Other card headlines are provided to avoid repetition, not as evidence. State the distinctive development of this card first; mention shared context only when needed. Include useful complementary details supported by the listed sources, and attribute source-specific claims when necessary. Do not invent differences, facts, or agreement. Return JSON {"title":"specific headline","summary":"2-3 concise sentences"}."""

def main():
 p=argparse.ArgumentParser()
 for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 byid={x["id"]:x for x in graph["sources"]}
 body={x["source_id"]:x["text"] for x in texts["sources"] if x.get("status")=="extracted_unverified" and len(x.get("text",""))>=800}
 cases=[c for c in meta["reviews"] if sum(s in body for s in c["source_ids"])>=2]
 ids=list(dict.fromkeys(s for c in cases for s in c["source_ids"] if s in body))
 out={"variant":"principal_developments_differential","sources":{},"contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Frozen corpus; not independent truth verification.","Source bodies truncated at 7000 characters.","Group membership requires validation against extracted developments."]}
 endpoint=os.environ["UBIK_LLM_ENDPOINT"];model=os.environ["UBIK_LLM_MODEL"];key=os.environ["UBIK_LLM_API_KEY"]
 def ask(prompt,payload):
  response,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
  out["calls"]+=1;usage_add(out["usage"],usage);return response
 for sid in ids:
  for attempt in range(3):
   try:
    answer=ask(EXTRACT,{"source_id":sid,"title":byid[sid]["title"],"article_body":body[sid][:7000]})
    ds=answer.get("developments")
    if answer.get("source_id")!=sid or not isinstance(ds,list) or any(not isinstance(d,dict) or not all(isinstance(d.get(k),str) for k in ("title","summary","evidence")) for d in ds):raise ValueError("invalid extraction schema")
    out["sources"][sid]=answer;write(a.output,out);break
   except Exception as e:
    if attempt==2:out["errors"].append({"stage":"extraction","source_id":sid,"error":str(e)[:200]});write(a.output,out)
 for ci,c in enumerate(cases):
  members=[s for s in c["source_ids"] if s in out["sources"]]
  atoms=[{"source_id":sid,"development_index":j,"title":d["title"],"summary":d["summary"]} for sid in members for j,d in enumerate(out["sources"][sid]["developments"])]
  context={"source_ids":members,"groups":[],"unassigned":[],"invalid":[]}
  valid={(d["source_id"],d["development_index"]) for d in atoms};used=set()
  try:
   answer=ask(GROUP,{"developments":atoms})
   for g in answer.get("groups",[]):
    raw=g.get("members",[])
    pairs=[(m.get("source_id"),m.get("development_index")) for m in raw if isinstance(m,dict)]
    if not pairs or len(pairs)!=len(raw) or len(set(pairs))!=len(pairs) or not set(pairs)<=valid or set(pairs)&used or len({s for s,j in pairs})!=len(pairs):
     context["invalid"].append(g);continue
    used.update(pairs)
    context["groups"].append({"focus":g.get("focus",""),"members":raw,"source_ids":[s for s,j in pairs],"type":"card" if len(pairs)>=2 else "standalone"})
  except Exception as e:out["errors"].append({"stage":"grouping","context":ci,"error":str(e)[:200]})
  for sid,j in sorted(valid-used):
   context["unassigned"].append({"source_id":sid,"development_index":j})
   context["groups"].append({"focus":out["sources"][sid]["developments"][j]["title"],"members":[{"source_id":sid,"development_index":j}],"source_ids":[sid],"type":"standalone","recovered":True})
  # Summarize all groups against their siblings, including standalones; persist checkpoints.
  for gi,g in enumerate(context["groups"]):
   evidence=[{"source_id":m["source_id"],**out["sources"][m["source_id"]]["developments"][m["development_index"]]} for m in g["members"]]
   others=[x["focus"] for k,x in enumerate(context["groups"]) if k!=gi]
   try:g["synthesis"]=ask(SUMMARIZE,{"focus":g["focus"],"evidence":evidence,"other_card_headlines":others})
   except Exception as e:out["errors"].append({"stage":"synthesis","context":ci,"group":gi,"error":str(e)[:200]})
  out["contexts"].append(context);write(a.output,out)
 out["summary"]={"eligible_sources":len(ids),"extracted_sources":len(out["sources"]),"contexts":len(out["contexts"]),"cards":sum(sum(g["type"]=="card" for g in c["groups"]) for c in out["contexts"]),"standalones":sum(sum(g["type"]=="standalone" for g in c["groups"]) for c in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
