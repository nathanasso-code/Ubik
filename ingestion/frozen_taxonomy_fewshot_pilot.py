"""Ubik: independent taxonomy few-shot A/B/C pilot on frozen DeepSeek news."""
import argparse, json, os, re
from collections import defaultdict
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ingestion.frozen_independent_qwen_deepseek import ask

SCHEMA = """Classify ONE source-grounded news item independently. Never assume knowledge of other news. Use a cross-domain descriptive grammar: domain, phenomenon, information_class (study/decision/event/process/statement/etc), reference_type, reference_label (the SPECIFIC study, act, episode or ongoing process, not a broad topic), reference_identifiers (only explicit DOI, official identifier, project name etc), actors, action, object, factual_claim (one precise assertion), relation_to_reference (method/result/decision/reaction/consequence/other), epistemic_status, uncertainty. Preserve differences between one study and its findings, and between a decision and reactions to that decision. A reaction may have the original decision as its reference, not a separate matrix. Never fabricate identifiers or actors. Use null or [] if unknown. Return ONLY JSON with exactly these fields: {"domain":"","phenomenon":"","information_class":"","reference_type":"","reference_label":"","reference_identifiers":[],"actors":[],"action":"","object":"","factual_claim":"","relation_to_reference":"","epistemic_status":"","uncertainty":""}."""
EXAMPLES = [
 {"input":{"title":"Parliament approves a revised transport bill","summary":"The national parliament passed bill 42/2026 revising freight safety rules."},"output":{"domain":"governance","phenomenon":"transport regulation","information_class":"legislative decision","reference_type":"legislative act","reference_label":"bill 42/2026 on freight safety","reference_identifiers":["42/2026"],"actors":["national parliament"],"action":"approves","object":"freight safety revision","factual_claim":"Parliament approved bill 42/2026 revising freight safety rules.","relation_to_reference":"decision","epistemic_status":"reported","uncertainty":""}},
 {"input":{"title":"Volcano eruption disrupts flights","summary":"A new eruptive episode at fictional Mount Luma on 12 May produced an ash plume and flight cancellations."},"output":{"domain":"earth science","phenomenon":"volcanic activity","information_class":"natural event","reference_type":"eruption episode","reference_label":"Mount Luma eruptive episode of 12 May","reference_identifiers":[],"actors":[],"action":"produces","object":"ash plume and flight cancellations","factual_claim":"The 12 May Mount Luma eruption produced ash and disrupted flights.","relation_to_reference":"consequence","epistemic_status":"reported","uncertainty":"year not specified"}},
 {"input":{"title":"New chip X7 announced","summary":"A manufacturer unveiled its X7 processor with a redesigned neural accelerator."},"output":{"domain":"technology","phenomenon":"processor development","information_class":"product announcement","reference_type":"product launch","reference_label":"X7 processor announcement","reference_identifiers":["X7"],"actors":["manufacturer"],"action":"unveils","object":"processor with neural accelerator","factual_claim":"The manufacturer unveiled the X7 processor with a redesigned neural accelerator.","relation_to_reference":"announcement","epistemic_status":"reported","uncertainty":"manufacturer unnamed"}},
 {"input":{"title":"Trial reports results for treatment Z","summary":"A clinical trial registered as DEMO-123 reports improved symptom scores for treatment Z."},"output":{"domain":"medicine","phenomenon":"clinical research","information_class":"research finding","reference_type":"clinical study","reference_label":"treatment Z clinical trial DEMO-123","reference_identifiers":["DEMO-123"],"actors":["clinical trial researchers"],"action":"reports","object":"improved symptom scores","factual_claim":"Trial DEMO-123 reports improved symptom scores for treatment Z.","relation_to_reference":"result","epistemic_status":"study finding","uncertainty":""}}
]
FIELDS = ["domain","phenomenon","information_class","reference_type","reference_label","reference_identifiers","actors","action","object","factual_claim","relation_to_reference","epistemic_status","uncertainty"]
def norm(s):
 return re.sub(r"\\s+"," ",re.sub(r"[^\\w\\s]"," ",str(s).lower())).strip()
def union_components(size, edges):
 parent=list(range(size))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,j in edges:
  a,b=find(i),find(j)
  if a!=b:parent[b]=a
 groups=defaultdict(list)
 for i in range(size):groups[find(i)].append(i)
 return list(groups.values())
def classify(news, model, count, usage):
 prompt=SCHEMA
 if count:prompt+="\\nEXAMPLES (illustrative only, unrelated to target news):\\n"+json.dumps(EXAMPLES[:count],ensure_ascii=False)
 response=ask(model,prompt,{"title":news["title"],"summary":news["summary"],"source_id":news["source_id"]},usage)
 if not isinstance(response,dict) or not all(k in response for k in FIELDS):raise ValueError("Incomplete taxonomy response")
 for field in ("reference_identifiers","actors"):
  if not isinstance(response[field],list):raise ValueError("Invalid "+field)
 for field in FIELDS:
  if field not in ("reference_identifiers","actors") and not isinstance(response[field],(str,type(None))):raise ValueError("Invalid "+field)
 return response
def build(news, labels, encoder):
 # Encode the reference separately from the claim. Taxonomy fields are not interchangeable.
 refs=[(x.get("reference_type") or "")+". "+(x.get("reference_label") or "")+". "+(x.get("phenomenon") or "") for x in labels]
 facts=[(x.get("action") or "")+". "+(x.get("object") or "")+". "+(x.get("factual_claim") or "") for x in labels]
 rv=encoder.encode(refs,normalize_embeddings=True,show_progress_bar=False)
 fv=encoder.encode(facts,normalize_embeddings=True,show_progress_bar=False)
 rs=cosine_similarity(rv);fs=cosine_similarity(fv)
 edges=[];decisions=[]
 for i in range(len(news)):
  for j in range(i+1,len(news)):
   a,b=labels[i],labels[j]
   ai={norm(x) for x in a["reference_identifiers"] if norm(x)}
   bi={norm(x) for x in b["reference_identifiers"] if norm(x)}
   same_id=bool(ai & bi)
   contradictory_ids=bool(ai and bi and not same_id)
   type_match=norm(a["reference_type"])==norm(b["reference_type"])
   ref_match=(same_id or (not contradictory_ids and type_match and rs[i,j]>=.80))
   if ref_match:edges.append((i,j))
   decisions.append({"a":news[i]["key"],"b":news[j]["key"],"reference_similarity":round(float(rs[i,j]),4),"fact_similarity":round(float(fs[i,j]),4),"same_identifier":bool(same_id),"reference_link":bool(ref_match)})
 matrices=[];reverse=defaultdict(lambda:{"news":[],"cards":[],"matrices":[]})
 for mi,indices in enumerate(union_components(len(news),edges)):
  # Only claim-equivalent facts join a card; keep differing aspects separate.
  card_groups=union_components(len(indices),[(u,v) for u in range(len(indices)) for v in range(u+1,len(indices)) if fs[indices[u],indices[v]]>=.87 and norm(labels[indices[u]]["relation_to_reference"])==norm(labels[indices[v]]["relation_to_reference"])])
  cards=[]
  for ci,positions in enumerate(card_groups):
   members=[indices[p] for p in positions];cid=f"m{mi}-c{ci}"
   source_ids=sorted({news[p]["source_id"] for p in members})
   card={"id":cid,"title":news[members[0]]["title"],"summary":labels[members[0]]["factual_claim"],"summary_status":"provisional_single_claim_not_multisource_synthesis","news_keys":[news[p]["key"] for p in members],"source_ids":source_ids,"claims":[{"news_key":news[p]["key"],"claim":labels[p]["factual_claim"],"source_id":news[p]["source_id"]} for p in members]}
   cards.append(card)
   for p in members:
    sid=news[p]["source_id"];reverse[sid]["news"].append(news[p]["key"]);reverse[sid]["cards"].append(cid)
  mid=f"m{mi}";source_ids=sorted({s for card in cards for s in card["source_ids"]})
  for sid in source_ids:reverse[sid]["matrices"].append(mid)
  matrices.append({"id":mid,"reference":labels[indices[0]]["reference_label"],"news_keys":[news[p]["key"] for p in indices],"source_ids":source_ids,"cards":cards})
 for sid,data in reverse.items():
  for k in data:data[k]=sorted(set(data[k]))
 assert sum(len(c["news_keys"]) for m in matrices for c in m["cards"])==len(news)
 assert {n["key"] for n in news}=={k for m in matrices for c in m["cards"] for k in c["news_keys"]}
 for m in matrices:assert set(m["source_ids"])=={sid for c in m["cards"] for sid in c["source_ids"]}
 return {"matrices":matrices,"source_index":dict(reverse),"pair_decisions":decisions}
def main():
 p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True);p.add_argument("--contexts",default="0,3");p.add_argument("--max-news",type=int,default=0);a=p.parse_args()
 prior=json.loads(a.input.read_text());contexts={int(x) for x in a.contexts.split(",")}
 news=[]
 for ctx in prior["arms"]["B_deepseek"]["contexts"]:
  if ctx["context"] not in contexts:continue
  by_id={}
  for card in ctx["cards"]:
   for s in card["sources"]:
    key=str(ctx["context"])+":"+s["news_id"]
    by_id[key]={"key":key,"source_id":s["source_id"],"title":s["original_title"],"summary":s["summary"],"context":ctx["context"]}
  news.extend(by_id.values())
 news=sorted(news,key=lambda n:(n["context"],n["key"]))
 if a.max_news:news=news[:a.max_news]
 assert news,"No frozen news found"
 encoder=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
 out={"experiment":"independent_taxonomy_fewshot","source":"frozen DeepSeek extraction, run 40090764027","news_count":len(news),"contexts":sorted(contexts),"schema":SCHEMA,"examples":EXAMPLES,"arms":{}}
 for n_examples in (0,2,4):
  name=f"examples_{n_examples}";usage={"calls":0};records=[];errors=[]
  for n in news:
   try:label=classify(n,os.environ["UBIK_LLM_MODEL"],n_examples,usage);status="ok"
   except Exception as exc:
    label=None;status="failed";errors.append({"news_key":n["key"],"error":str(exc)[:300]})
   records.append({"news":n,"classification":label,"status":status})
  valid=[r for r in records if r["classification"] is not None]
  # Build matrices independently for each original context; never cross an unrelated context boundary.
  contexts_out=[]
  for context in sorted(contexts):
   subset=[r for r in valid if r["news"]["context"]==context]
   if subset:
    built=build([r["news"] for r in subset],[r["classification"] for r in subset],encoder)
    contexts_out.append({"context":context,**built})
  out["arms"][name]={"usage":usage,"errors":errors,"records":records,"contexts":contexts_out,"coverage":{"classified":len(valid),"expected":len(news),"omitted_keys":[r["news"]["key"] for r in records if r["status"]!="ok"]},"totals":{"matrices":sum(len(c["matrices"]) for c in contexts_out),"cards":sum(sum(len(m["cards"]) for m in c["matrices"]) for c in contexts_out)}}
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2,default=lambda v: v.item() if hasattr(v,"item") else str(v)))
 print(json.dumps({k:{"coverage":v["coverage"],"totals":v["totals"],"calls":v["usage"]["calls"]} for k,v in out["arms"].items()},ensure_ascii=False))
if __name__=="__main__":main()
