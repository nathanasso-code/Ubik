"""Provider-agnostic LLM semantic analysis adapter, offline by default.

Optional OpenAI-compatible HTTP endpoint requires explicit --execute and credentials.
Outputs remain review-only. No calls are made during CI or module import.
"""
import argparse,json,os,urllib.request
from pathlib import Path
from ingestion.semantic_relation_contract import validate_relation
from ingestion.hierarchical_category_contract import validate_hierarchy

SYSTEM=("You analyze relationships among news texts, not factual truth. "
 "Return one JSON object with keys document_a_id, document_b_id, event_relation, semantic_relation, "
 "evidence (two or more objects with document_id and verbatim quote), "
 "category_a and category_b (each an object with levels: general-to-specific list of label and verbatim evidence_quote). "
 "Use uncertain relations and short category paths when insufficient evidence. "
 "Do not invent quotes, events or conclusions.")
def evaluate(result,sources):
    relation=validate_relation(result,sources)
    cats={}
    for k,doc_id in (("category_a",result.get("document_a_id")),("category_b",result.get("document_b_id"))):
        cats[k]=validate_hierarchy(result.get(k),sources.get(doc_id,""))
    return {"relation":relation,"categories":cats,
      "accepted_for_review":relation.get("accepted",False) and all(x.get("accepted",False) for x in cats.values()),
      "automatically_published":False}
def build_messages(a,b):
    return [{"role":"system","content":SYSTEM},
      {"role":"user","content":json.dumps({"document_a":a,"document_b":b},ensure_ascii=False)}]
def request_analysis(messages,endpoint,model,key,timeout=40):
    if not endpoint.startswith("https://"):raise ValueError("Only HTTPS endpoints allowed")
    if not key:raise ValueError("Missing API key")
    data=json.dumps({"model":model,"messages":messages,"response_format":{"type":"json_object"},
      "temperature":0}).encode()
    req=urllib.request.Request(endpoint,data=data,headers={"Authorization":"Bearer "+key,
      "Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=timeout) as response:
        body=json.load(response)
    return json.loads(body["choices"][0]["message"]["content"]),body.get("usage",{})
def run(queue,documents,limit=5,execute=False,endpoint=None,model=None,key=None):
    byurl={d["url"]:d for d in documents if d.get("url")}
    results=[]
    for pair in queue.get("queue",[])[:max(0,limit)]:
        a,b=byurl.get(pair["url_a"]),byurl.get(pair["url_b"])
        if not a or not b:
            results.append({"pair_id":pair["pair_id"],"status":"missing_source"});continue
        def text(d):
            return next((str(d[k]) for k in ("full_text","text","content","description","summary","title") if d.get(k)),"")
        sources={"a":text(a),"b":text(b)}
        if not all(sources.values()):
            results.append({"pair_id":pair["pair_id"],"status":"missing_text"});continue
        if not execute:
            results.append({"pair_id":pair["pair_id"],"status":"ready_for_llm",
              "available_text_characters":{"a":len(sources["a"]),"b":len(sources["b"])}})
            continue
        try:
            proposal,usage=request_analysis(build_messages({"id":"a","title":a.get("title"),"text":sources["a"]},
                {"id":"b","title":b.get("title"),"text":sources["b"]}),endpoint,model,key)
            results.append({"pair_id":pair["pair_id"],"status":"analyzed",
               "validation":evaluate(proposal,sources),"usage":usage,"model":model})
        except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as exc:
            results.append({"pair_id":pair["pair_id"],"status":"analysis_error","error_type":type(exc).__name__})
    return {"schema_version":1,"mode":"api" if execute else "dry_run","results":results,
      "coverage":{"selected":len(results),"ready":sum(x["status"]=="ready_for_llm" for x in results),
      "analyzed":sum(x["status"]=="analyzed" for x in results),
      "accepted_for_review":sum(x.get("validation",{}).get("accepted_for_review",False) for x in results)},
      "limitations":["Dry-run performs no LLM inference.","Evidence grounding is substring validation, not proof of semantic correctness.",
      "No automatic merges, taxonomy publishing or factual truth claims."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("--queue",type=Path,required=True)
    p.add_argument("--hybrid",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int,default=5);p.add_argument("--execute",action="store_true")
    p.add_argument("--endpoint",default=os.environ.get("UBIK_LLM_ENDPOINT",""))
    p.add_argument("--model",default=os.environ.get("UBIK_LLM_MODEL",""))
    args=p.parse_args()
    if args.execute and (not args.endpoint or not args.model or not os.environ.get("UBIK_LLM_API_KEY")):
        p.error("Execution requires endpoint, model and UBIK_LLM_API_KEY")
    queue=json.loads(args.queue.read_text());hybrid=json.loads(args.hybrid.read_text())
    result=run(queue,hybrid.get("documents",[]),args.limit,args.execute,args.endpoint,args.model,
        os.environ.get("UBIK_LLM_API_KEY"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
