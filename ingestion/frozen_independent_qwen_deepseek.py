"""Independent Qwen/Qwen and DeepSeek/DeepSeek arms over identical frozen news and source texts."""
import argparse,json,os
from pathlib import Path
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ingestion.llm_semantic_adapter import request_analysis

EXTRACT="""For each supplied source-grounded news item, independently produce (1) a short, specific, factual summary of that news item and (2) one to three exact contiguous verbatim excerpts from article_body supporting it. Keep distinct news items distinct at extraction. Do not import conclusions from any other summary. If evidence is insufficient, say so and return no quotes. Return only JSON {"items":[{"id":"...","summary":"...","quotes":["..."]}]}. Preserve every ID. No invented facts or quotes."""
REVIEW="""You receive an entire embedding-connected component of summarized news from the same context. Some summaries are substantively equivalent; others differ only in insignificant details; still others differ in substantive facts, events, decisions or statements. Your task is to identify ONLY the substantive factual differences that justify independent cards. Merge summaries that are substantively equivalent even when they differ in wording, marginal details or perspective. If multiple news items describe the same substantially autonomous, substantive event and are similar in their differences from the rest, group them in one card. Independently distinguish genuinely different news and group any that are equivalent in that difference. Do not force a common nucleus or split merely because of different quotations. Decide on factual substance, not topical proximity. For each separate card, explicitly identify its distinguishing substantive fact; do not invent any. Include each input ID exactly once, including singletons. Return ONLY JSON {"groups":[{"ids":["..."],"title":"...","summary":"...","reason":"..."}]}."""
def ask(model,prompt,data,usage):
 result,meta=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(data,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],model,os.environ["UBIK_LLM_API_KEY"],timeout=180)
 usage["calls"]+=1
 if not isinstance(result,dict):raise ValueError("Invalid JSON")
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument("grounded",type=Path);p.add_argument("texts",type=Path);p.add_argument("--output",type=Path,required=True);p.add_argument("--threshold",type=float,default=.68);a=p.parse_args()
 base=json.loads(a.grounded.read_text());corpus=json.loads(a.texts.read_text())
 bodies={x["source_id"]:x.get("text","") for x in corpus["sources"] if x.get("text")}
 encoder=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
 output={"experiment":"independent_end_to_end_models","threshold":a.threshold,"prompt_extract":EXTRACT,"prompt_review":REVIEW,"arms":{}}
 for arm,model in [("A_qwen",os.environ["UBIK_QWEN_MODEL"]),("B_deepseek",os.environ["UBIK_LLM_MODEL"])]:
  result={"model":model,"contexts":[],"errors":[],"usage":{"calls":0}}
  for ctx in base["contexts"]:
   items=ctx["news"];extracted={};by_source=defaultdict(list)
   for n in items:by_source[n["source_id"]].append(n)
   for sid,news in by_source.items():
    body=bodies.get(sid,"")
    if not body:
     result["errors"].append({"context":ctx["context"],"source_id":sid,"phase":"missing_body"});continue
    try:
     response=ask(model,EXTRACT,{"article_body":body[:14000],"news":[{"id":n["id"],"title":n["title"]} for n in news]},result["usage"])
     for item in response.get("items",[]):
      if not isinstance(item,dict) or item.get("id") not in {n["id"] for n in news}:continue
      summary=item.get("summary","")
      if not isinstance(summary,str) or not summary.strip():continue
      verified=[]
      for quote in item.get("quotes",[]):
       if isinstance(quote,str) and quote and quote in body:
        start=body.find(quote);verified.append({"text":quote,"start":start,"end":start+len(quote)})
      extracted[item["id"]]={"summary":summary.strip(),"passages":verified,"evidence_status":"verified" if verified else "missing"}
    except Exception as e:result["errors"].append({"context":ctx["context"],"source_id":sid,"phase":"extract","error":str(e)[:300]})
   # Retry omissions one news at a time, using the same model and original source text.
   # This distinguishes incomplete batch responses from unavailable source material.
   for n in items:
    if n["id"] in extracted:continue
    body=bodies.get(n["source_id"],"")
    if not body:continue
    try:
     retry=ask(model,EXTRACT,{"article_body":body[:14000],"news":[{"id":n["id"],"title":n["title"]}]},result["usage"])
     candidate=next((x for x in retry.get("items",[]) if isinstance(x,dict) and x.get("id")==n["id"] and isinstance(x.get("summary"),str) and x["summary"].strip()),None)
     if candidate:
      verified=[]
      for quote in candidate.get("quotes",[]):
       if isinstance(quote,str) and quote and quote in body:
        start=body.find(quote);verified.append({"text":quote,"start":start,"end":start+len(quote)})
      extracted[n["id"]]={"summary":candidate["summary"].strip(),"passages":verified,"evidence_status":"verified" if verified else "missing","extraction_mode":"individual_retry"}
    except Exception as e:result["errors"].append({"context":ctx["context"],"source_id":n["source_id"],"news_id":n["id"],"phase":"individual_retry","error":str(e)[:300]})
   # No fallback to the other model or prior DeepSeek summaries: exclude missing extractions from model comparisons.
   valid=[n for n in items if n["id"] in extracted]
   omitted=[n["id"] for n in items if n["id"] not in extracted]
   if not valid:
    result["contexts"].append({"context":ctx["context"],"cards":[],"embedding_components":[],"omitted_ids":omitted});continue
   sentences=[n["title"]+". "+extracted[n["id"]]["summary"] for n in valid]
   vectors=encoder.encode(sentences,normalize_embeddings=True,show_progress_bar=False)
   similarities=cosine_similarity(vectors);parent=list(range(len(valid)))
   def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
   for i in range(len(valid)):
    for j in range(i+1,len(valid)):
     if valid[i]["source_id"]!=valid[j]["source_id"] and similarities[i,j]>=a.threshold:
      ri,rj=find(i),find(j)
      if ri!=rj:parent[rj]=ri
   components=defaultdict(list)
   for i in range(len(valid)):components[find(i)].append(i)
   cards=[];reviews=[]
   for component in components.values():
    payload=[{"id":valid[i]["id"],"title":valid[i]["title"],"summary":extracted[valid[i]["id"]]["summary"],"source_id":valid[i]["source_id"]} for i in component]
    groups=[];status="singleton"
    if len(component)>1:
     try:
      response=ask(model,REVIEW,{"news":payload},result["usage"])
      seen=set()
      for g in response.get("groups",[]):
       ids=g.get("ids",[])
       if not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)) or any(x not in {n["id"] for n in payload} or x in seen for x in ids):continue
       groups.append((ids,g));seen.update(ids)
      if seen!={n["id"] for n in payload}:raise ValueError("Review did not partition all input IDs")
      status="reviewed"
     except Exception as e:
      result["errors"].append({"context":ctx["context"],"phase":"review","ids":[n["id"] for n in payload],"error":str(e)[:300]})
      groups=[([n["id"]],{}) for n in payload];status="review_failed"
    else:groups=[([payload[0]["id"]],{})]
    reviews.append({"input_ids":[n["id"] for n in payload],"status":status,"groups":[g[0] for g in groups]})
    for ids,g in groups:
     members=[next(n for n in valid if n["id"]==nid) for nid in ids]
     sources=[{"news_id":n["id"],"source_id":n["source_id"],"original_title":n["title"],**extracted[n["id"]]} for n in members]
     cards.append({"id":f"{arm}-{ctx['context']}-{len(cards)}","news_ids":ids,"title":g.get("title") or members[0]["title"],"summary":g.get("summary") or extracted[ids[0]]["summary"],"reason":g.get("reason"),"sources":sources})
   result["contexts"].append({"context":ctx["context"],"input_count":len(items),"extracted_count":len(valid),"omitted_ids":omitted,"embedding_components":[[valid[i]["id"] for i in c] for c in components.values()],"reviews":reviews,"cards":cards})
  result["totals"]={"input_news":sum(len(c["news"]) for c in base["contexts"]),"extracted_news":sum(c.get("extracted_count",0) for c in result["contexts"]),"cards":sum(len(c["cards"]) for c in result["contexts"]),"components":sum(len(c["embedding_components"]) for c in result["contexts"]),"verified_passages":sum(len(s["passages"]) for c in result["contexts"] for card in c["cards"] for s in card["sources"])}
  output["arms"][arm]=result
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2))
 print(json.dumps({k:v["totals"] for k,v in output["arms"].items()}))
if __name__=="__main__":main()
