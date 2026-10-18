"""Qwen review of the same frozen cases, restricted to substantial original texts."""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("You are a rigorous news event identity editor. Follow TWO ordered stages. "
"STAGE 1: for EVERY source independently extract a structured event fingerprint: "
"source_id, subject (who), action (what happened), object (to whom/what), "
"event_date (not publication date; null if unknown), place (null if unknown), "
"result_or_consequence (null if unknown), central_development, "
"information_quality (substantive or insufficient), and ambiguity. "
"Use only supplied text; do not infer missing fields. A long generic template or "
"news bulletin without identifiable concrete stories is INSUFFICIENT. "
"STAGE 2: compare these fingerprints, not mere topical similarity. "
"Group sources only when they describe the SAME specific central development. "
"Shared subjects, conflict, theme, background, causal relationship, or reactions "
"to an event do NOT alone establish identity. Separate distinct announcements, "
"responses, interviews, meetings, analyses, and follow-up events. "
"Different publication dates or complementary details do not necessarily mean "
"different events. Leave uncertain sources standalone and explain uncertainty. "
"Return valid JSON with source_facts:[{source_id,subject,action,object,event_date,"
"place,result_or_consequence,central_development,information_quality,ambiguity}], "
"cards:[{source_ids:[...],reason:string}], "
"related_events:[{source_ids:[...],relation:string}], uncertainties:[string]. "
"Each source must appear in source_facts exactly once. "
"No verbatim quotations required. Do not invent facts or automatically publish.")

def run(graph,metadata,texts,requester=request_analysis,endpoint="",model="",key="",max_calls=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    results=[];skipped=[];errors=[]
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:
            skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_substantial_texts"});continue
        if len(results)+len(errors)>=max_calls:break
        payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],
                 "text":extracted[sid]["text"][:7000]} for sid in ids]}
        try:
            answer,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=60)
            used=set();cards=[];invalid=[]
            for c in answer.get("cards",[]):
                if not isinstance(c,dict):continue
                members=c.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=set(ids) or used.intersection(members):
                    invalid.append({"members":members,"reason":"invalid_membership"});continue
                used.update(members)
                cards.append({"source_ids":sorted(members),"reason":c.get("reason",""),
                              "status":"qwen_text_decision_unverified"})
            results.append({"source_ids":ids,"original_case_ids":case["source_ids"],"cards":cards,
                "source_facts":answer.get("source_facts",[]),
                "related_events":answer.get("related_events",[]),
                "standalone_source_ids":sorted(set(ids)-used),"invalid_groups":invalid,
                "uncertainties":answer.get("uncertainties",[]),"usage":usage})
        except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as exc:
            errors.append({"source_ids":ids,"error_type":type(exc).__name__})
    return {"summary":{"metadata_reviewed_cases":len(metadata["reviews"]),
             "substantial_text_sources":len(extracted),"text_reviewed_cases":len(results),
             "skipped_cases":len(skipped),"errors":len(errors),
             "provisional_text_cards":sum(len(x["cards"]) for x in results),
             "llm_calls":len(results)+len(errors)},
            "reviews":results,"skipped":skipped,"errors":errors,
            "limitations":["Only available substantial texts are reviewed; no imputation for missing articles.",
             "No quotation validator or semantic veto is applied; manual editorial review is required.",
             "No automatic publication or accuracy claim."]}

def main():
    p=argparse.ArgumentParser()
    for name in ("graph","metadata","texts"):p.add_argument(name,type=Path)
    p.add_argument("--output",required=True,type=Path);p.add_argument("--max-calls",type=int,default=20)
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM configuration")
    result=run(*[json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")],
        endpoint=endpoint,model=model,key=key,max_calls=a.max_calls)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("TEXT_QWEN",json.dumps(result["summary"]))
if __name__=="__main__":main()
