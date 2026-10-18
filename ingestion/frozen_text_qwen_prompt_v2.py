"""V2 prompt A/B: event identity with explicit relations and abstention."""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_text_qwen_review import FIELDS,validate_fact

SYSTEM="""You are an exacting news editor. For each supplied article, first read the TITLE and identify the ONE main claim the title makes. Then inspect ONLY the body text that actually belongs to this article, excluding navigation, recommendations, unrelated headlines, and boilerplate. If the body does not substantiate that title, say insufficient. Do not rely on prior knowledge or invent any facts.
For EVERY source return exactly ONE source_facts object with source_id, subject, action, object, event_date, place, result_or_consequence, central_development, information_quality ('substantive' or 'insufficient'), ambiguity. Dates are dates of events, not publication dates. Use null for unknown fields. An opinion piece, podcast or video may have a main editorial development, but without relevant content do not infer the story from nearby links. Do not confuse claims with confirmed facts: 'Trump claimed a ceasefire' is NOT 'a ceasefire occurred'.
Then compare those fingerprints and distinguish FOUR relations:
SAME_EVENT = identical concrete action/decision/outcome, with matching essential actor and object; reporting the same announcement with complementary details qualifies.
REACTION = an actor comments on or responds to another event; it is a distinct development, NOT SAME_EVENT.
FOLLOW_UP = a subsequent meeting, announcement, interview, implementation or consequence; distinct event.
TOPIC_ONLY = same actors or subject matter, but no demonstrated event identity.
Only SAME_EVENT sources may share a card. REACTION, FOLLOW_UP, and TOPIC_ONLY must NOT merge. When in doubt, leave standalone and record uncertainty. An insufficient source must remain standalone.
Before grouping, check for contradictions in subject, action, object, event date, and the distinction between action and reaction. Do not group on semantic similarity alone.
Return ONE valid JSON object with source_facts:[...], cards:[{source_ids:[...],reason:string}], related_events:[{source_ids:[...],relation:string}], uncertainties:[string]. Include every source exactly once in source_facts. No invented facts and no automatic publication."""

def run(graph,metadata,texts,requester=request_analysis,endpoint="",model="",key="",max_calls=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    results=[];skipped=[];errors=[];calls=0
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:
            skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_substantial_texts"});continue
        if calls>=max_calls:
            skipped.append({"source_ids":ids,"reason":"call_budget"});continue
        payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],
                 "article_body":extracted[sid]["text"][:7000]} for sid in ids]}
        calls+=1
        try:
            answer,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
                endpoint,model,key,timeout=90)
            facts=answer.get("source_facts")
            if not isinstance(facts,list) or len(facts)!=len(ids):
                raise ValueError("fingerprint_count_mismatch")
            if len({f.get("source_id") for f in facts if isinstance(f,dict)})!=len(ids):
                raise ValueError("fingerprint_duplicate_or_missing")
            validated=[validate_fact(f,f["source_id"]) for f in facts]
            if set(f["source_id"] for f in validated)!=set(ids):
                raise ValueError("fingerprint_unknown_ids")
            eligible={f["source_id"] for f in validated if f["information_quality"]=="substantive" and not f["ambiguity"]}
            used=set();cards=[];invalid=[]
            for card in answer.get("cards",[]):
                if not isinstance(card,dict):continue
                members=card.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=eligible or used.intersection(members):
                    invalid.append({"members":members,"reason":"invalid_membership_or_insufficient_source"});continue
                used.update(members)
                cards.append({"source_ids":sorted(members),"reason":card.get("reason",""),
                              "status":"qwen_text_decision_unverified"})
            results.append({"source_ids":ids,"original_case_ids":case["source_ids"],"cards":cards,
                "source_facts":validated,"related_events":answer.get("related_events",[]),
                "standalone_source_ids":sorted(set(ids)-used),"invalid_groups":invalid,
                "uncertainties":answer.get("uncertainties",[]),"usage":usage})
        except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as exc:
            errors.append({"source_ids":ids,"error_type":type(exc).__name__,"message":str(exc)[:150]})
    return {"summary":{"metadata_reviewed_cases":len(metadata["reviews"]),
            "substantial_text_sources":len(extracted),"text_reviewed_cases":len(results),
            "skipped_cases":len(skipped),"errors":len(errors),
            "provisional_text_cards":sum(len(x["cards"]) for x in results),
            "llm_calls":calls},
            "reviews":results,"skipped":skipped,"errors":errors,
            "limitations":["Single API call per context, two ordered prompt stages.",
              "Title anchoring and schema validation do not guarantee factual accuracy.",
              "No automatic publication."]}

def main():
    p=argparse.ArgumentParser()
    for name in ("graph","metadata","texts"):p.add_argument(name,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--max-calls",type=int,default=20)
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM configuration")
    result=run(*[json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")],
        endpoint=endpoint,model=model,key=key,max_calls=a.max_calls)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("TEXT_QWEN_SINGLE",json.dumps(result["summary"]))
if __name__=="__main__":main()
