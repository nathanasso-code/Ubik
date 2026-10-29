import json, os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

folder=Path("data/taxonomy-pilot")
few=json.loads((folder/"fewshot-results.json").read_text())
prior=json.loads((folder/"adjudication-results.json").read_text())
arm=few["arms"]["examples_4"]
context=next(c for c in arm["contexts"] if c["context"]==3)
records={r["news"]["key"]:r for r in arm["records"] if r["status"]=="ok" and r["news"]["context"]==3}
groups=prior["provisional_groups"]
by_key={k:i for i,g in enumerate(groups) for k in g["news_keys"]}
best={}
for pair in context["pair_decisions"]:
 a,b=pair["a"],pair["b"]
 if a not in by_key or b not in by_key or by_key[a]==by_key[b]:continue
 if pair["reference_similarity"]<0.64:continue
 key=tuple(sorted([by_key[a],by_key[b]]))
 if key not in best or pair["reference_similarity"]>best[key]["reference_similarity"]:best[key]=pair
selected=sorted(best.values(),key=lambda x:-x["reference_similarity"])[:28]
prompt="Compare two specific news referents, not just themes. Return JSON with relation (IDENTITY, BELONGING, CORRELATION, UNCERTAIN), confidence (high, medium, low), shared_reference, evidence, reason. IDENTITY: same exact identifiable act or event. BELONGING: direct reaction, consequence, component, or aspect of same identifiable act or event. CORRELATION: different acts or events sharing topic. UNCERTAIN: evidence insufficient. Never merge merely because Russia, Ukraine, actors, or sanctions overlap. Prefer uncertainty over unsupported merger."
out={"experiment":"second_pass","selected":len(selected),"results":[],"errors":[],"calls":0}
target=folder/"second-pass-results.json"
for pair in selected:
 a,b=pair["a"],pair["b"]
 data={"a":{"title":records[a]["news"]["title"],"summary":records[a]["news"]["summary"],"classification":records[a]["classification"]},"b":{"title":records[b]["news"]["title"],"summary":records[b]["news"]["summary"],"classification":records[b]["classification"]}}
 try:
  answer,meta=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(data,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
  out["calls"]+=1
  rel=str(answer.get("relation","")).upper()
  if rel not in ("IDENTITY","BELONGING","CORRELATION","UNCERTAIN"):raise ValueError("invalid relation")
  out["results"].append({"pair":pair,"group_a":by_key[a],"group_b":by_key[b],"judgment":answer,"relation":rel})
 except Exception as exc:out["errors"].append({"pair":pair,"error":str(exc)[:250]})
 target.write_text(json.dumps(out,ensure_ascii=False,indent=2))
parent=list(range(len(groups)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for item in out["results"]:
 if item["relation"] not in ("IDENTITY","BELONGING"):continue
 if item["judgment"].get("confidence")!="high" or not item["judgment"].get("evidence"):continue
 i,j=find(item["group_a"]),find(item["group_b"])
 if i!=j:parent[j]=i
clusters={}
for i,g in enumerate(groups):clusters.setdefault(find(i),[]).append(i)
out["provisional_groups"]=[{"previous_group_indices":v,"news_keys":sorted({k for i in v for k in groups[i]["news_keys"]})} for v in clusters.values()]
out["summary"]={"before":len(groups),"after":len(clusters),"calls":out["calls"],"errors":len(out["errors"]),"judgments":{r:sum(x["relation"]==r for x in out["results"]) for r in ("IDENTITY","BELONGING","CORRELATION","UNCERTAIN")}}
target.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out["summary"]))
