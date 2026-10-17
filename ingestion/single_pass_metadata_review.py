"""Single-pass metadata event adjudication: one LLM call per bounded component.

The retrieval graph only defines review cases, NEVER automatically merged cards.
Oversized connected components are deferred (not silently split into overlapping
windows). All results are provisional, with per-case checkpoint and usage.
"""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.critical_metadata_case_review import SYSTEM

def run(data,requester=request_analysis,endpoint="",model="",key="",max_calls=12,max_sources=18,checkpoint=None):
    docs={s["id"]:s for s in data["sources"]}
    edges=data["candidate_pairs"]
    contexts=sorted(data["review_contexts"],key=lambda c:(-max((e["score"] for e in edges if e["a"] in c["source_ids"] and e["b"] in c["source_ids"]),default=0),-len(c["source_ids"])))
    results=[];errors=[];deferred=[]
    for case in contexts:
        ids=case["source_ids"]
        if len(ids)>max_sources:
            deferred.append({"source_ids":ids,"reason":"oversized_component_requires_manual_or_hierarchical_review"});continue
        if len(results)+len(errors)>=max_calls:break
        payload={"sources":[docs[i] for i in ids],"candidate_edges":[e for e in edges if e["a"] in ids and e["b"] in ids]}
        try:
            answer,usage=requester([{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=35)
            cards=[];used=set();invalid=[]
            for card in answer.get("cards",[]):
                if not isinstance(card,dict):continue
                members=card.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(members)!=len(set(members)) or not set(members)<=set(ids) or used.intersection(members):
                    invalid.append(members);continue
                used.update(members)
                cards.append({"source_ids":sorted(members),"central_development":card.get("central_development",""),"reason":card.get("reason",""),"status":"metadata_only_provisional"})
            results.append({"source_ids":ids,"cards":cards,"standalone_source_ids":sorted(set(ids)-used),
                            "invalid_groups":invalid,"uncertainties":answer.get("uncertainties",[]),"usage":usage})
        except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as e:
            errors.append({"source_ids":ids,"error_type":type(e).__name__})
        if checkpoint:
            checkpoint.parent.mkdir(parents=True,exist_ok=True)
            checkpoint.write_text(json.dumps({"reviewed":results,"errors":errors,"deferred":deferred},ensure_ascii=False,indent=2)+"\n")
    return {"summary":{"sources":len(docs),"candidate_edges":len(edges),"review_contexts":len(contexts),
      "reviewed_cases":len(results),"errors":len(errors),"deferred_oversized":len(deferred),
      "unreviewed_cases":len(contexts)-len(results)-len(errors)-len(deferred),
      "provisional_cards":sum(len(r["cards"]) for r in results),
      "llm_calls_attempted":len(results)+len(errors)},
      "reviews":results,"errors":errors,"deferred":deferred,
      "limitations":["Review components are not cards and are not automatically merged.",
        "Oversized cases are deferred, not fragmented into overlapping windows.",
        "Metadata-only outputs are provisional, not verified facts.",
        "The call cap leaves remaining contexts unreviewed; never count them as negatives."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--max-calls",type=int,default=12)
    p.add_argument("--max-sources",type=int,default=18);a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM configuration")
    out=run(json.loads(a.input.read_text()),endpoint=endpoint,model=model,key=key,max_calls=a.max_calls,
        max_sources=a.max_sources,checkpoint=a.output.with_suffix(".checkpoint.json"))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("SINGLE_PASS",json.dumps(out["summary"]))
    for r in out["reviews"]:print("CASE",json.dumps({"source_ids":r["source_ids"],"cards":r["cards"]},ensure_ascii=False))
if __name__=="__main__":main()
