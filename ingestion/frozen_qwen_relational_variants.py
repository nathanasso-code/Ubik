"""Controlled frozen-corpus relation-first experiments. No changes to production."""
import argparse,json,os,re
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add

COMPACT="""You receive sourced fine identities, not original articles. For EACH source independently, group complementary microfacts about the SAME substantive development into composed identities, preserving all important qualifiers and distinctions. Never merge distinct events, actors' distinct reactions, or contradictory claims. Return JSON {"sources":[{"source_id":"...","identities":[{"text":"self-contained composed development","fine_claim_ids":["c0"]}]}]}. Every fine claim must be accounted for exactly once, including peripheral ones; do not invent IDs."""
RELATE="""Build an evidence-backed relationship matrix from the supplied identities. A 'letter' is a canonical specific substantive development, not a mere shared topic. Match claims across sources only for the SAME development. Preserve unique developments and important disagreements. Return JSON {"developments":[{"id":"d1","description":"...","members":[{"source_id":"...","claim_ids":["c0"]}]}]}. Cover EVERY claim exactly once; include singleton developments. Never invent source or claim IDs."""
COMPOSE="""Compose the fewest editorially coherent DISTINCT news cards without hiding substantive autonomous developments. Cards must represent developments, not individual details. Sources can appear in multiple cards, including as corroborating sources. Preserve factual distinctions and attribute disagreements. Return JSON {"cards":[{"title":"...","summary":"2-4 factual sentences","development_ids":["d1"]}],"excluded_development_ids":[{"id":"d2","reason":"duplicate|peripheral|insufficient"}]}. Cover every development in a card or explicit exclusion. Never invent IDs."""
ONE_DIFF="""Use the relation matrix. Apply a proposed SOURCE-PAIR heuristic: sources differing by at most ONE distinct canonical development should preferentially share a card; pairs differing by MORE THAN ONE new development should preferentially start separate cards. Difference means symmetric difference of development-ID sets, not number of wording variations. This is a SOFT heuristic, not transitive equivalence: do not join incompatible chains merely via a bridging source. Keep all important developments and source support; allow a source to appear in multiple cards. Produce few coherent news cards, not one per letter. Return JSON {"cards":[{"title":"...","summary":"2-4 factual sentences","development_ids":["d1"]}],"excluded_development_ids":[{"id":"d2","reason":"duplicate|peripheral|insufficient"}]}. Cover every development in a card or explicit exclusion."""
def main():
 p=argparse.ArgumentParser();p.add_argument("identity_result",type=Path);p.add_argument("--variant",choices=["fine_relations","composed_relations","one_difference"],required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 data=json.loads(a.identity_result.read_text());out={"variant":a.variant,"contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Uses frozen extracted claims, not source article text.","Editorial and identity matching judgments require human review."]}
 def ask(prompt,payload):
  for attempt in range(2):
   try:
    response,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
    out["calls"]+=1;usage_add(out["usage"],usage);return response
   except Exception as e:
    if attempt:raise
 for ci,ctx in enumerate(data["contexts"]):
  claims=[{"id":"c"+str(k),"source_id":sid,"text":x["text"]} for k,(sid,x) in enumerate((sid,x) for sid in ctx["source_ids"] for x in data["sources"].get(sid,{}).get("identities",[]) if isinstance(x,dict) and isinstance(x.get("text"),str))]
  item={"context":ci,"tag":ctx.get("tag"),"source_ids":ctx["source_ids"],"input_claims":len(claims),"cards":[],"uncovered_claim_ids":[],"errors":[]}
  try:
   if a.variant=="composed_relations":
    compact=ask(COMPACT,{"claims":claims});ids={c["id"] for c in claims};seen=set();composed=[]
    for s in compact.get("sources",[]):
     sid=s.get("source_id")
     if sid not in ctx["source_ids"]:continue
     for ent in s.get("identities",[]):
      refs=ent.get("fine_claim_ids",[])
      if not isinstance(refs,list) or not refs or any(r not in ids or r in seen for r in refs):continue
      if any(next(c["source_id"] for c in claims if c["id"]==r)!=sid for r in refs):continue
      seen.update(refs);composed.append({"id":"k"+str(len(composed)),"source_id":sid,"text":ent.get("text",""),"fine_claim_ids":refs})
    for c in claims:
     if c["id"] not in seen:composed.append({"id":"k"+str(len(composed)),"source_id":c["source_id"],"text":c["text"],"fine_claim_ids":[c["id"]]})
    atoms=composed;item["composed_identities"]=composed
   else:atoms=claims
   relation=ask(RELATE,{"claims":atoms});valid={x["id"]:x for x in atoms};seen=set();devs=[]
   for d in relation.get("developments",[]):
    refs=[r for m in d.get("members",[]) for r in m.get("claim_ids",[]) if r in valid and valid[r]["source_id"]==m.get("source_id")]
    if not refs or len(refs)!=len(set(refs)) or any(r in seen for r in refs):continue
    seen.update(refs);devs.append({"id":"d"+str(len(devs)),"description":d.get("description",""),"claim_ids":refs,"source_ids":list(dict.fromkeys(valid[r]["source_id"] for r in refs))})
   for atom in atoms:
    if atom["id"] not in seen:devs.append({"id":"d"+str(len(devs)),"description":atom["text"],"claim_ids":[atom["id"]],"source_ids":[atom["source_id"]]})
   item["developments"]=devs
   source_sets={sid:[d["id"] for d in devs if sid in d["source_ids"]] for sid in ctx["source_ids"]}
   item["source_developments"]=source_sets
   if a.variant=="one_difference":
    pairs=[{"a":a0,"b":b0,"different":len(set(source_sets[a0])^set(source_sets[b0])),"shared":len(set(source_sets[a0])&set(source_sets[b0]))} for i,a0 in enumerate(ctx["source_ids"]) for b0 in ctx["source_ids"][i+1:]]
    item["source_pair_distances"]=pairs
   response=ask(ONE_DIFF if a.variant=="one_difference" else COMPOSE,{"developments":devs,"source_developments":source_sets,"pair_distances":item.get("source_pair_distances",[])})
   validdev={d["id"]:d for d in devs};covered=set()
   for card in response.get("cards",[]):
    refs=card.get("development_ids",[])
    if not isinstance(refs,list) or not refs or any(r not in validdev for r in refs):continue
    covered.update(refs)
    sources=list(dict.fromkeys(s for r in refs for s in validdev[r]["source_ids"]))
    item["cards"].append({"title":card.get("title",""),"summary":card.get("summary",""),"development_ids":refs,"source_ids":sources})
   exclusions=[e for e in response.get("excluded_development_ids",[]) if isinstance(e,dict) and e.get("id") in validdev and e.get("id") not in covered]
   item["excluded_developments"]=exclusions
   accounted=covered|{e["id"] for e in exclusions}
   item["uncovered_development_ids"]=[d["id"] for d in devs if d["id"] not in accounted]
   item["uncovered_claim_ids"]=[r for d in devs if d["id"] not in accounted for atom in d["claim_ids"] for r in valid[atom].get("fine_claim_ids",[atom])]
   item["covered_sources"]=list(dict.fromkeys(s for card in item["cards"] for s in card["source_ids"]))
  except Exception as e:
   item["errors"].append(str(e)[:300]);out["errors"].append({"context":ci,"error":str(e)[:300]});item["uncovered_claim_ids"]=[c["id"] for c in claims]
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"variant":a.variant,"contexts":len(out["contexts"]),"input_sources":len(data["sources"]),"input_claims":sum(c["input_claims"] for c in out["contexts"]),"cards":sum(len(c["cards"]) for c in out["contexts"]),"sources_in_cards":len(set(s for c in out["contexts"] for s in c.get("covered_sources",[]))),"uncovered_claims":sum(len(c["uncovered_claim_ids"]) for c in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
