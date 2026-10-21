"""Two-pass per context: faithful source interpretation, then pertinent differential cards."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_atoms_verified import write,usage_add
READ="""Independently interpret EACH article body. Ignore navigation, related links, sidebar headlines and unrelated bulletins. Return exactly one entry per supplied ID. For each: quality substantive or insufficient; a faithful 2-3 sentence summary; one specific central focus; up to 3 substantive distinctive facts, not trivial details. Preserve decisions, reactions, outcomes and attribution. Do not create cards. JSON {"sources":[{"source_id":"exact","quality":"substantive|insufficient","summary":"text or empty","central_focus":"text or empty","contributions":["specific factual contribution"]}]}."""
COMPOSE="""Organize these independently interpreted sources into a SMALL set of PERTINENT news cards. Each card must tell a coherent, specific and DISTINCT part of the story, supported by its listed sources. Shared background and repeated source IDs are permitted, but cannot justify redundant cards. Combine different sources when their contributions support one meaningful development; do not merge unrelated developments. Do not split one event into trivial details. A source may support multiple cards for different contributions. Preserve uncovered important facts in a separate list. For each card provide a distinctive focus, a concise factual 2-3 sentence summary, and exact supporting source IDs. Return JSON {"cards":[{"title":"specific","distinctive_focus":"what this card uniquely adds","summary":"2-3 factual sentences","source_ids":["exact"]}],"uncovered":["important uncovered fact"],"uncertainties":["..."]}."""
def main():
 p=argparse.ArgumentParser()
 for x in ("graph","metadata","texts"):p.add_argument(x,type=Path)
 p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 graph=json.loads(a.graph.read_text());meta=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
 titles={x["id"]:x["title"] for x in graph["sources"]}
 bodies={x["source_id"]:x["text"] for x in texts["sources"] if x.get("status")=="extracted_unverified" and len(x.get("text",""))>=800}
 cases=[c for c in meta["reviews"] if sum(s in bodies for s in c["source_ids"])>=2]
 out={"variant":"two_pass_focus_differential","contexts":[],"errors":[],"calls":0,"usage":{},"limitations":["Frozen texts may include page noise.","Source attribution checked structurally, not factually.","Each context requires two LLM calls; incomplete interpretations are flagged."]}
 def ask(prompt,payload):
  answer,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=120)
  out["calls"]+=1;usage_add(out["usage"],usage);return answer
 for i,c in enumerate(cases):
  ids=[s for s in c["source_ids"] if s in bodies]
  item={"source_ids":ids,"sources":[],"missing_sources":[],"cards":[],"invalid_cards":[],"uncovered":[],"uncertainties":[]}
  try:
   ans=ask(READ,{"sources":[{"id":s,"title":titles[s],"article_body":bodies[s][:7000]} for s in ids]})
   seen=set()
   for entry in ans.get("sources",[]):
    if not isinstance(entry,dict) or entry.get("source_id") not in ids or entry["source_id"] in seen:continue
    seen.add(entry["source_id"]);item["sources"].append(entry)
   item["missing_sources"]=sorted(set(ids)-seen)
   if item["missing_sources"]:out["errors"].append({"context":i,"stage":"read","missing":item["missing_sources"]})
   write(a.output,out)
   if not item["sources"]:raise ValueError("no interpreted sources")
   response=ask(COMPOSE,{"sources":item["sources"]})
   eligible={x["source_id"] for x in item["sources"] if x.get("quality")=="substantive"}
   for card in response.get("cards",[]):
    refs=card.get("source_ids",[])
    if not isinstance(refs,list) or not refs or len(set(refs))!=len(refs) or not set(refs)<=eligible or not all(isinstance(card.get(k),str) and card[k].strip() for k in ("title","summary","distinctive_focus")):item["invalid_cards"].append(card);continue
    item["cards"].append(card)
   item["uncovered"]=response.get("uncovered",[])
   item["uncertainties"]=response.get("uncertainties",[])
  except Exception as e:out["errors"].append({"context":i,"stage":"processing","error":str(e)[:240]})
  out["contexts"].append(item);write(a.output,out)
 out["summary"]={"contexts":len(out["contexts"]),"sources":sum(len(x["sources"]) for x in out["contexts"]),"cards":sum(len(x["cards"]) for x in out["contexts"]),"multi_source_cards":sum(sum(len(c["source_ids"])>1 for c in x["cards"]) for x in out["contexts"]),"missing_sources":sum(len(x["missing_sources"]) for x in out["contexts"]),"errors":len(out["errors"]),"calls":out["calls"]}
 write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
