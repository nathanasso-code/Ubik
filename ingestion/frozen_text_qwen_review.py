"""Two separate Qwen calls: title-anchored per-source extraction, then event comparison."""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

EXTRACT_SYSTEM = """You are extracting the MAIN news development of ONE article.
The supplied title is the primary anchor: identify the central development the title refers to, and verify it against the article body. Do not switch to related articles, navigation, recommendations, sidebars, background, or unrelated events mentioned on the page. Do not invent facts or use general world knowledge.
Return JSON object with keys source_id, subject, action, object, event_date, place, result_or_consequence, central_development, information_quality, ambiguity. Use null for unknown fields.
information_quality MUST be 'substantive' only if the provided body actually supports the headline's specific event with concrete details. Otherwise use 'insufficient', especially for video pages without transcripts, generic bulletin descriptions, boilerplate, or mismatch between title and body. Explain the issue in ambiguity. Exactly ONE fingerprint for the supplied source; never output multiple events or a list of source_facts."""
COMPARE_SYSTEM = """You are an event identity editor. Input contains independently extracted, title-anchored event fingerprints, NOT full article pages. Group ONLY sources reporting the SAME specific central development. A shared actor, broad topic, conflict, cause, announcement and its later reaction, meeting, interview or analysis is not enough. Distinct developments must remain separate; complementary details or different publication dates alone do not imply distinct events. Any source with information_quality != substantive MUST remain standalone. If identity cannot be established, abstain.
Return JSON object: cards:[{source_ids:[...],reason:string}], related_events:[{source_ids:[...],relation:string}], uncertainties:[string]. No invented details and no automatic publication."""

FIELDS=("subject","action","object","event_date","place","result_or_consequence","central_development","information_quality","ambiguity")

def validate_fact(answer,sid):
    if not isinstance(answer,dict) or answer.get("source_id")!=sid:
        raise ValueError("fingerprint_source_id_mismatch")
    if any(k not in answer for k in FIELDS):
        raise ValueError("fingerprint_missing_fields")
    if answer["information_quality"] not in ("substantive","insufficient"):
        raise ValueError("fingerprint_invalid_quality")
    if answer["information_quality"]=="substantive" and not all(
        isinstance(answer.get(k),str) and answer[k].strip()
        for k in ("subject","action","central_development")):
        raise ValueError("fingerprint_missing_central_event")
    return {k:answer[k] for k in ("source_id",)+FIELDS}

def run(graph,metadata,texts,requester=request_analysis,endpoint="",model="",key="",max_calls=100):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    results=[];skipped=[];errors=[];calls=0
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:
            skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_substantial_texts"});continue
        if calls+len(ids)+1>max_calls:
            skipped.append({"source_ids":ids,"reason":"call_budget"});continue
        facts=[];usage=[];extraction_errors=[]
        for sid in ids:
            payload={"source_id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],
                     "article_body":extracted[sid]["text"][:7000]}
            try:
                answer,u=requester([{"role":"system","content":EXTRACT_SYSTEM},
                    {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
                    endpoint,model,key,timeout=60)
                facts.append(validate_fact(answer,sid));usage.append({"phase":"extract","source_id":sid,"usage":u})
            except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as exc:
                extraction_errors.append({"source_id":sid,"error_type":type(exc).__name__})
            calls+=1
        if extraction_errors:
            errors.append({"source_ids":ids,"phase":"extraction","details":extraction_errors})
            continue
        eligible=[f["source_id"] for f in facts if f["information_quality"]=="substantive"]
        cards=[];invalid=[];related=[];uncertainties=[]
        if len(eligible)>=2:
            try:
                answer,u=requester([{"role":"system","content":COMPARE_SYSTEM},
                    {"role":"user","content":json.dumps({"source_facts":facts},ensure_ascii=False)}],
                    endpoint,model,key,timeout=60)
                usage.append({"phase":"compare","usage":u})
                used=set()
                for card in answer.get("cards",[]):
                    if not isinstance(card,dict):continue
                    members=card.get("source_ids",[])
                    if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=set(eligible) or used.intersection(members):
                        invalid.append({"members":members,"reason":"invalid_membership_or_insufficient_source"});continue
                    used.update(members)
                    cards.append({"source_ids":sorted(members),"reason":card.get("reason",""),
                                  "status":"qwen_text_decision_unverified"})
                related=answer.get("related_events",[])
                uncertainties=answer.get("uncertainties",[])
            except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as exc:
                errors.append({"source_ids":ids,"phase":"comparison","error_type":type(exc).__name__})
                calls+=1
                continue
            calls+=1
        used={sid for card in cards for sid in card["source_ids"]}
        results.append({"source_ids":ids,"original_case_ids":case["source_ids"],"cards":cards,
            "source_facts":facts,"related_events":related,
            "standalone_source_ids":sorted(set(ids)-used),"invalid_groups":invalid,
            "uncertainties":uncertainties,"usage":usage})
    return {"summary":{"metadata_reviewed_cases":len(metadata["reviews"]),
             "substantial_text_sources":len(extracted),"text_reviewed_cases":len(results),
             "skipped_cases":len(skipped),"errors":len(errors),
             "provisional_text_cards":sum(len(x["cards"]) for x in results),
             "llm_calls":calls,"extraction_calls":sum(len(x["source_ids"]) for x in results)+sum(len(x.get("details",[])) for x in errors if x.get("phase")=="extraction")},
            "reviews":results,"skipped":skipped,"errors":errors,
            "limitations":["Extraction and comparison use separate API calls.",
             "Title-anchored extraction and deterministic schema checks do not verify factual truth.",
             "No automatic publication or accuracy claim."]}

def main():
    p=argparse.ArgumentParser()
    for name in ("graph","metadata","texts"):p.add_argument(name,type=Path)
    p.add_argument("--output",required=True,type=Path);p.add_argument("--max-calls",type=int,default=100)
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM configuration")
    result=run(*[json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")],
        endpoint=endpoint,model=model,key=key,max_calls=a.max_calls)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("TEXT_QWEN",json.dumps(result["summary"]))
if __name__=="__main__":main()
