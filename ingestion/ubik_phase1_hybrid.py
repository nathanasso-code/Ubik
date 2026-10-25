"""Single frozen phase-1 hybrid run. Gold never used in retrieval or judging."""
import json,os,itertools,urllib.request,urllib.error,time
from pathlib import Path
from sentence_transformers import SentenceTransformer
from ingestion.ubik_json_response import parse_json_response
ROOT=Path("data/taxonomy-pilot")
SYSTEM=("You are an independent event-identity judge. Decide whether two descriptions from different sources refer to the SAME concrete real-world event or act. The descriptions can emphasize different facets of the same act, but thematic similarity, shared actors, related consequences, reactions, or temporal proximity are NOT sufficient. A reaction to an act is distinct from the act. Two distinct official actions are distinct even if both concern sanctions, diesel, or Russia. Use only the two supplied event records. If evidence is insufficient to establish identity, answer uncertain rather than guessing. Do not infer hidden facts or use any other comparisons. Return only valid JSON with keys \"decision\" and \"reason\". Decision must be one of \"equivalent\", \"distinct\", \"uncertain\". Reason must be a brief explanation (max 40 words).")
FIELDS=("qualified_id","actor","action","object","time","actuality","evidence")
def main():
 data=json.loads((ROOT/"v4-sonnet55.json").read_text())
 ev={e["qualified_id"]:e for s in data["sources"] for e in s["events"]}
 ids=sorted(ev);assert len(ids)==33
 model=SentenceTransformer("intfloat/multilingual-e5-small",device="cpu")
 vec=model.encode(["passage: "+str(ev[i].get("action") or "")+" "+str(ev[i].get("object") or "") for i in ids],normalize_embeddings=True,convert_to_numpy=True,show_progress_bar=False)
 sim=vec@vec.T; idx={k:i for i,k in enumerate(ids)}
 def similarity(a,b):return float(sim[idx[a],idx[b]])
 candidates=set()
 for a in ids:
  ranked=sorted((b for b in ids if b!=a and b.split(":")[0]!=a.split(":")[0]),key=lambda b:(-similarity(a,b),b))
  for b in ranked[:5]:candidates.add(tuple(sorted((a,b))))
 pairs=sorted(candidates,key=lambda p:(-similarity(*p),p))
 output=ROOT/"phase1-hybrid-sonnet55.json"
 result={"method":"e5-small","judge_model":"anthropic/claude-sonnet-5.5","candidate_pairs":len(pairs),"candidate_ids":[list(p) for p in pairs],"judgments":[],"supplemental":[],"errors":[]}
 def save():output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 save()
 def judge(pair,kind):
  a,b=pair
  payload={"model":"anthropic/claude-sonnet-5.5","messages":[{"role":"system","content":SYSTEM},{"role":"user","content":"Event A:\n"+json.dumps({k:ev[a].get(k) for k in FIELDS},ensure_ascii=False)+"\n\nEvent B:\n"+json.dumps({k:ev[b].get(k) for k in FIELDS},ensure_ascii=False)+"\n\nDecide whether A and B describe the same concrete event. Output only JSON."}],"response_format":{"type":"json_object"},"max_tokens":200}
  record={"pair":[a,b],"similarity":similarity(a,b),"kind":kind}
  try:
   req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["UBIK_LLM_API_KEY"],"Content-Type":"application/json"},method="POST")
   with urllib.request.urlopen(req,timeout=120) as resp:body=json.loads(resp.read())
   raw=body["choices"][0]["message"].get("content","")
   record["raw"]=raw
   parsed=parse_json_response(raw)
   decision=parsed.get("decision")
   record["decision"]=decision if decision in ("equivalent","distinct","uncertain") else "uncertain"
   record["reason"]=str(parsed.get("reason",""))[:500]
   record["usage"]=body.get("usage",{})
  except Exception as exc:
   record["decision"]="uncertain";record["error"]=str(exc)[:400]
  result["judgments" if kind=="candidate" else "supplemental"].append(record);save()
 for pair in pairs:judge(pair,"candidate")
 # Conservative preliminary groups, used only to generate targeted confirmations.
 decisions={tuple(r["pair"]):r["decision"] for r in result["judgments"]}
 positives={p for p,v in decisions.items() if v=="equivalent"}
 negatives={p for p,v in decisions.items() if v=="distinct"}
 groups=[{x} for x in ids]
 def allowed(g,h):
  return not any(tuple(sorted((a,b))) in negatives for a in g for b in h)
 for p in sorted(positives,key=lambda p:(-similarity(*p),p)):
  ga=next(g for g in groups if p[0] in g);gb=next(g for g in groups if p[1] in g)
  if ga is gb:continue
  count=sum(a in ga and b in gb or b in ga and a in gb for a,b in positives)
  if allowed(ga,gb) and (len(ga)==len(gb)==1 or count>=2):
   groups.remove(ga);groups.remove(gb);groups.append(ga|gb)
 supplemental=[]
 for a in ids:
  ga=next(g for g in groups if a in g)
  if len(ga)!=1:continue
  options=[]
  for g in groups:
   if len(g)<2 or g is ga or not allowed(ga,g):continue
   confirmed=[b for b in g if tuple(sorted((a,b))) in positives]
   if len(confirmed)!=1:continue
   unchecked=[b for b in g if tuple(sorted((a,b))) not in decisions]
   if unchecked:
    b=sorted(unchecked,key=lambda b:(-similarity(a,b),b))[0]
    options.append(tuple(sorted((a,b))))
  if options:
   supplemental.append(sorted(options,key=lambda p:(-similarity(*p),p))[0])
 supplemental=sorted(set(supplemental),key=lambda p:(-similarity(*p),p))[:33]
 for pair in supplemental:judge(pair,"supplemental")
 # Save complete decisions for independent, post-hoc gold evaluation.
 allrecords=result["judgments"]+result["supplemental"]
 result["total_judged"]=len(allrecords)
 result["usage_totals"]={k:sum((r.get("usage") or {}).get(k,0) or 0 for r in allrecords) for k in ("prompt_tokens","completion_tokens","total_tokens")}
 save()
 print(json.dumps({"candidates":len(pairs),"supplemental":len(result["supplemental"]),"decisions":{x:sum(r["decision"]==x for r in allrecords) for x in ("equivalent","distinct","uncertain")},"usage":result["usage_totals"]}))
if __name__=="__main__":main()
