"""Two controlled frozen-corpus clustering strategies: identity incidence vs repaired source cards."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

TOPIC="""Name the general news context shared by these candidate article titles. This is a retrieval tag, NOT an event identity. Return JSON {"tag":"short descriptive topic label"}."""
IDENTITY="""Read ONE article independently. Its general context tag is supplied only for orientation. Extract ALL distinct substantive news developments actually asserted or reported in the article; no minimum or maximum number. Give each identity one faithful, self-contained sentence. Do not split synonyms or mere details of the same development into separate identities. Do not include navigation, boilerplate, generic background, unsupported inferences, or a decision merely referenced to explain a reaction unless the article substantively reports that decision too. Decisions, statements about decisions, and reactions by different actors are separate identities. Return JSON {"source_id":"exact ID","identities":[{"text":"one standalone faithful sentence","evidence":"short supporting verbatim excerpt from article"}],"quality":"substantive|insufficient"}. An empty array is allowed. Do not force identities."""
NORMALIZE="""Within ONE general context, assign canonical event identities to independently extracted statements. Two statements share a canonical ID only when they assert the SAME specific development, allowing different wording and detail. Same topic, same subject of debate, opposite reactions, common cause, or chronological follow-up are NOT identity. A source may participate in multiple identities. Do not connect identities transitively merely because one source mentions both. Return JSON {"groups":[{"identity":"precise canonical one-sentence identity","members":[{"source_id":"...","identity_index":0}]}],"uncertain":[]}. Include each input statement in at most one group. Singletons are allowed. Never invent IDs or indices."""
SOURCE_EXTRACT="""Read ONE news source independently. Return JSON {"source_id":"exact ID","quality":"substantive|insufficient","summary":"faithful brief report","primary":{"actor":"...","action":"...","object":"...","event_type":"decision|reaction|report|finding|event|analysis|other"},"identities":["each substantive distinct development, one sentence"]}. Distinguish primary development from background and reactions. Do not invent."""
SOURCE_GROUP="""Compare ALL independently extracted source representations in this topic. Propose cards of sources primarily reporting the same specific news development. Differences in depth do not invalidate identity. Different reactions to a decision are separate. Return JSON {"cards":[{"source_ids":["..."],"shared_development":"one sentence"}]}. Empty cards is valid. A source must not appear in multiple cards in this source-centered variant."""
REPAIR="""Review proposed cards skeptically. For EACH proposal, identify the largest defensible coherent subset of source IDs that primarily report the SAME specific development. A card with an outlier should be repaired, not discarded wholesale. Split into multiple subsets if justified. Different reaction actors are not identical. Return JSON {"cards":[{"source_ids":["..."],"shared_development":"..."}],"rejected_source_ids":["..."],"reason":"..."}; do not force cards, minimum two members per card. Never include any source ID more than once."""
def main():
 p=argparse.ArgumentParser()
 for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
 p.add_argument("--variant",choices=("identity","repair"),required=True)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 byid={x["id"]:x for x in graph["sources"]}
 body={x["source_id"]:x["text"] for x in texts["sources"] if x.get("status")=="extracted_unverified" and len(x.get("text",""))>=800}
 cases=[c for c in meta["reviews"] if sum(s in body for s in c["source_ids"])>=2]
 ids=list(dict.fromkeys(s for c in cases for s in c["source_ids"] if s in body))
 endpoint=os.environ["UBIK_LLM_ENDPOINT"];model=os.environ["UBIK_LLM_MODEL"];key=os.environ["UBIK_LLM_API_KEY"]
 out={"variant":a.variant,"sources":{},"contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Review-only proposals, not ground truth.","Input articles truncated at 7000 characters."]}
 def ask(prompt,payload):
  answer,u=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
  out["calls"]+=1;usage_add(out["usage"],u);return answer
 # A single context tag per case, derived from titles only, never used as merge evidence.
 tags={}
 if a.variant=="identity":
  for i,c in enumerate(cases):
   members=[s for s in c["source_ids"] if s in body]
   try:
    tag=ask(TOPIC,{"titles":[byid[s]["title"] for s in members]}).get("tag","general")
    tags[i]=tag if isinstance(tag,str) else "general"
   except Exception as e:
    tags[i]="general";out["errors"].append({"stage":"tag","case":i,"error":str(e)[:160]})
 # Independent source extraction with immediate durable checkpoint.
 for sid in ids:
  context=next((tags.get(i,"general") for i,c in enumerate(cases) if sid in c["source_ids"]),"general")
  prompt=IDENTITY if a.variant=="identity" else SOURCE_EXTRACT
  for attempt in range(2):
   try:
    s=byid[sid]
    ans=ask(prompt,{"source_id":sid,"title":s["title"],"context_tag":context,"article_body":body[sid][:7000]})
    if ans.get("source_id")!=sid:raise ValueError("source_id mismatch")
    if a.variant=="identity":
     atoms=ans.get("identities")
     if not isinstance(atoms,list) or any(not isinstance(x,dict) or not isinstance(x.get("text"),str) or not isinstance(x.get("evidence"),str) for x in atoms):raise ValueError("invalid identities")
    elif not isinstance(ans.get("primary"),dict) or not isinstance(ans.get("identities"),list):raise ValueError("invalid primary")
    out["sources"][sid]=ans;write(a.output,out);break
   except Exception as e:
    if attempt==1:out["errors"].append({"stage":"extraction","source_id":sid,"error":str(e)[:160]});write(a.output,out)
 for i,c in enumerate(cases):
  members=[s for s in c["source_ids"] if s in out["sources"]]
  result={"source_ids":members,"tag":tags.get(i),"cards":[],"singletons":[],"invalid":[]}
  try:
   if a.variant=="identity":
    atoms=[{"source_id":sid,"identity_index":j,"text":x["text"]} for sid in members for j,x in enumerate(out["sources"][sid]["identities"])]
    ans=ask(NORMALIZE,{"tag":tags[i],"statements":atoms})
    valid={(x["source_id"],x["identity_index"]) for x in atoms}
    assigned=set()
    for g in ans.get("groups",[]):
     entries=g.get("members",[])
     pairs=[(x.get("source_id"),x.get("identity_index")) for x in entries if isinstance(x,dict)]
     if not pairs or len(set(pairs))!=len(pairs) or not set(pairs)<=valid or set(pairs)&assigned or len({x[0] for x in pairs})!=len(pairs):
      result["invalid"].append(g);continue
     assigned.update(pairs)
     group={"identity":g.get("identity"),"source_ids":[x[0] for x in pairs],"members":entries}
     if len(pairs)>1:result["cards"].append(group)
     else:result["singletons"].append(group)
    result["unassigned_atoms"]=[{"source_id":s,"identity_index":j} for s,j in sorted(valid-assigned)]
   else:
    ans=ask(SOURCE_GROUP,{"sources":[out["sources"][s] for s in members]})
    proposals=ans.get("cards",[])
    if proposals:
     repaired=ask(REPAIR,{"sources":[out["sources"][s] for s in members],"proposed_cards":proposals})
     candidates=repaired.get("cards",[])
    else:candidates=[]
    used=set()
    for card in candidates:
     mids=card.get("source_ids",[])
     if not isinstance(mids,list) or len(mids)<2 or len(set(mids))!=len(mids) or not set(mids)<=set(members) or set(mids)&used:
      result["invalid"].append(card);continue
     result["cards"].append(card);used.update(mids)
    result["singletons"]=[s for s in members if s not in used]
  except Exception as e:out["errors"].append({"stage":"context","case":i,"error":str(e)[:160]})
  out["contexts"].append(result);write(a.output,out)
 out["summary"]={"eligible_sources":len(ids),"extracted_sources":len(out["sources"]),"contexts":len(out["contexts"]),"cards":sum(len(x["cards"]) for x in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
