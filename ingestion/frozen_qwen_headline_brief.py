"""Fresh per-source headline/brief extraction and three controlled composition variants."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add
READ="""Read ONE original article. Ignore navigation, sidebar, related-story links and incidental mentions. Extract the FUNDAMENTAL NEWS DEVELOPMENTS substantively reported in its MAIN text. Each development needs a specific factual TITLE and SHORT SUMMARY (1-3 sentences). Combine method, numbers, quotes, context and immediate consequences of the SAME development into its summary. Do NOT generate a separate development for each detail or quote. Preserve genuinely independent developments, including distinct decisions and material reactions. No fixed number: one is often enough; zero if the body is not substantive. Never invent. Return JSON {"source_id":"exact","quality":"substantive|insufficient","news":[{"title":"...","summary":"...","evidence":"short verbatim supporting excerpt"}]}."""
RELATE="""Compare extracted news developments across sources, NOT all microfacts. Identify SAME specific development across sources, even when complementary details differ. Do not equate merely topical or chronological relatedness. Return JSON {"groups":[{"members":["n0","n2"],"shared_development":"..."}]}. Each news ID exactly once; singleton groups allowed."""
COMPOSE="""Create the FEWEST coherent DISTINCT substantive news cards that preserve independent developments. Group complementary developments into one coherent news story; do not create cards for details. Keep original sources as support including corroborating sources. A source may appear on multiple cards. Return JSON {"cards":[{"title":"...","summary":"2-4 factual sentences","group_ids":["g0"]}],"excluded_group_ids":[{"id":"g1","reason":"peripheral|duplicate|insufficient"}]}. Account for every group. Do not invent IDs."""
ONE_DIFF="""Compose news cards using this SOFT source-pair rule: sources differing by AT MOST ONE canonical fundamental development should preferentially be grouped; sources differing by MORE THAN ONE should preferentially be split. Difference is symmetric difference of group ID sets. Do not assume transitivity through a bridge source. Preserve genuinely separate stories and all material information. Return JSON {"cards":[{"title":"...","summary":"2-4 factual sentences","group_ids":["g0"]}],"excluded_group_ids":[{"id":"g1","reason":"peripheral|duplicate|insufficient"}]}. Account for every group. Do not invent IDs."""
SHARED="""Prefer grouping sources with at least TWO shared canonical fundamental developments, but use it as a soft signal only; one strongly shared development can suffice. Do not merge unrelated stories. Create the FEWEST coherent DISTINCT substantive news cards, and retain source support. Return JSON {"cards":[{"title":"...","summary":"2-4 factual sentences","group_ids":["g0"]}],"excluded_group_ids":[{"id":"g1","reason":"peripheral|duplicate|insufficient"}]}. Account for every group."""
def ask(prompt,payload,out):
 last=None
 for attempt in range(2):
  try:
   result,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
   out["calls"]+=1;usage_add(out["usage"],usage)
   if not isinstance(result,dict):raise ValueError("non-object JSON")
   return result
  except Exception as exc:last=exc
 raise last
def main():
 p=argparse.ArgumentParser();p.add_argument("graph",type=Path);p.add_argument("metadata",type=Path);p.add_argument("texts",type=Path);p.add_argument("--phase",choices=["extract","compose"],required=True);p.add_argument("--extraction",type=Path);p.add_argument("--variant",choices=["semantic","one_difference","shared_two"]);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 titles={s["id"]:s["title"] for s in graph["sources"]}
 bodies={s["source_id"]:s["text"] for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
 cases=[c for c in meta["reviews"] if sum(s in bodies for s in c["source_ids"])>=2]
 if a.phase=="extract":
  out={"phase":"fresh_headline_brief_extraction","sources":{},"contexts":[{"source_ids":[s for s in c["source_ids"] if s in bodies]} for c in cases],"errors":[],"calls":0,"usage":{}}
  ids=list(dict.fromkeys(s for c in cases for s in c["source_ids"] if s in bodies))
  for sid in ids:
   try:
    result=ask(READ,{"source_id":sid,"title":titles[sid],"article_body":bodies[sid][:7000]},out)
    if result.get("source_id")!=sid or not isinstance(result.get("news"),list):raise ValueError("invalid source response")
    valid=[n for n in result["news"] if isinstance(n,dict) and all(isinstance(n.get(k),str) and n[k].strip() for k in ("title","summary","evidence"))]
    out["sources"][sid]={"source_id":sid,"quality":result.get("quality","substantive"),"news":valid,"title":titles[sid]}
   except Exception as exc:out["errors"].append({"source_id":sid,"error":str(exc)[:240]})
   write(a.output,out)
  out["summary"]={"sources_expected":len(ids),"sources_extracted":len(out["sources"]),"fundamental_news":sum(len(s["news"]) for s in out["sources"].values()),"errors":len(out["errors"]),"calls":out["calls"]}
  write(a.output,out);print(json.dumps(out["summary"]));return
 if not a.extraction or not a.variant:p.error("compose requires --extraction and --variant")
 extraction=json.loads(a.extraction.read_text())
 out={"phase":"fresh_headline_brief_composition","variant":a.variant,"contexts":[],"errors":[],"calls":0,"usage":{}}
 for ci,ctx in enumerate(extraction["contexts"]):
  ids=ctx["source_ids"];news=[{"id":"n"+str(k),"source_id":sid,"title":n["title"],"summary":n["summary"]} for k,(sid,n) in enumerate((sid,n) for sid in ids for n in extraction["sources"].get(sid,{}).get("news",[]))]
  item={"context":ci,"source_ids":ids,"news":news,"groups":[],"cards":[],"uncovered_news_ids":[],"errors":[]}
  try:
   if not news:
    item["errors"].append("no extracted news");out["contexts"].append(item);write(a.output,out);continue
   response=ask(RELATE,{"news":news},out);valid={n["id"]:n for n in news};seen=set();groups=[]
   for g in response.get("groups",[]):
    if not isinstance(g,dict):continue
    members=g.get("members",[])
    if not isinstance(members,list) or not members or len(set(members))!=len(members) or any(m not in valid or m in seen for m in members):continue
    seen.update(members);groups.append({"id":"g"+str(len(groups)),"members":members,"source_ids":list(dict.fromkeys(valid[m]["source_id"] for m in members)),"shared_development":g.get("shared_development","")})
   for n in news:
    if n["id"] not in seen:groups.append({"id":"g"+str(len(groups)),"members":[n["id"]],"source_ids":[n["source_id"]],"shared_development":n["title"]})
   item["groups"]=groups;source_sets={sid:[g["id"] for g in groups if sid in g["source_ids"]] for sid in ids};item["source_groups"]=source_sets
   pairs=[{"source_a":a0,"source_b":b0,"shared":len(set(source_sets[a0])&set(source_sets[b0])),"different":len(set(source_sets[a0])^set(source_sets[b0]))} for i,a0 in enumerate(ids) for b0 in ids[i+1:]]
   item["pair_metrics"]=pairs;write(a.output,out)
   prompt={"semantic":COMPOSE,"one_difference":ONE_DIFF,"shared_two":SHARED}[a.variant]
   result=ask(prompt,{"groups":groups,"news":news,"source_groups":source_sets,"pair_metrics":pairs},out)
   valid_groups={g["id"]:g for g in groups};covered=set()
   for card in result.get("cards",[]):
    if not isinstance(card,dict):continue
    refs=card.get("group_ids",[])
    if not isinstance(refs,list) or not refs or any(r not in valid_groups for r in refs):continue
    covered.update(refs)
    item["cards"].append({"title":card.get("title",""),"summary":card.get("summary",""),"group_ids":refs,"source_ids":list(dict.fromkeys(s for r in refs for s in valid_groups[r]["source_ids"]))})
   excluded=[e for e in result.get("excluded_group_ids",[]) if isinstance(e,dict) and e.get("id") in valid_groups and e["id"] not in covered]
   item["excluded_groups"]=excluded;covered.update(e["id"] for e in excluded)
   item["uncovered_group_ids"]=[g["id"] for g in groups if g["id"] not in covered]
   item["uncovered_news_ids"]=[n for g in groups if g["id"] not in covered for n in g["members"]]
   item["sources_in_cards"]=list(dict.fromkeys(s for card in item["cards"] for s in card["source_ids"]))
  except Exception as exc:item["errors"].append(str(exc)[:240]);out["errors"].append({"context":ci,"error":str(exc)[:240]});item["uncovered_news_ids"]=[n["id"] for n in news]
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"variant":a.variant,"contexts":len(out["contexts"]),"cards":sum(len(c["cards"]) for c in out["contexts"]),"sources_in_cards":len(set(s for c in out["contexts"] for s in c.get("sources_in_cards",[]))),"uncovered_news":sum(len(c["uncovered_news_ids"]) for c in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
