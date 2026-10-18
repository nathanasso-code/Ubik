"""Controlled A/B: primary proposition versus integrated article synthesis, then Qwen grouping."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

COMMON="""Read only the actual article content supplied for each source. Page navigation, unrelated headlines, suggested articles, and boilerplate are NOT evidence about the article. A title is a clue, not proof. Preserve attribution: a person's claim is not an established occurrence. If the text is insufficient (including bulletins or videos without substantive transcripts), say so. Never invent information.
FIRST complete a separate representation for EVERY source. SECOND compare ONLY those representations, not the raw pages. Group sources only if their PRIMARY informational contribution is the SAME concrete development. Shared topic, actors, context, background, secondary details, reactions, and follow-ups are insufficient for grouping. Leave uncertain sources separate. Return valid JSON, include every source exactly once. All group members must be substantive."""
PROMPTS={
"A":"""FIRST extract EXACTLY ONE primary, source-supported proposition for each article, with the actor and the nature of the action or statement explicitly identified. Add up to four secondary propositions only when informative. Do not confuse a report of a decision with a response to that decision. If a page truly contains several independent equally central stories, set quality='insufficient' and explain in uncertainty rather than arbitrarily merging unrelated items. Source object fields: source_id,quality ('substantive'|'insufficient'), primary ('one concise proposition' or null), actor (string or null), kind ('action'|'statement'|'finding'|'opinion'|'other' or null), secondary (array of propositions), uncertainty (string or null).
SECOND group based only on primary propositions, using secondary information solely to express relatedness.
Return JSON {"sources":[{"source_id":"...","quality":"substantive","primary":"...","actor":"...","kind":"action","secondary":[],"uncertainty":null}],"cards":[{"source_ids":["..."],"reason":"..."}],"related_events":[],"uncertainties":[]}.""",
"B":"""FIRST produce a faithful, coherent short SYNTHESIS of the main news communicated by EACH source, approximately 2-4 sentences, retaining the essential actors, actions, decisions, attribution, and necessary context. Write it naturally as a compact news summary, not as a list of facts or subject-action-object fields. Do not overemphasize background, tangential mentions, or reactions if they are not the central development. If substantive text is absent, set quality='insufficient' and summary=null. Source object fields: source_id, quality ('substantive'|'insufficient'), summary (string or null), uncertainty (string or null).
SECOND compare ONLY the source summaries, not the raw pages, to group sources reporting the SAME concrete central news development. Summaries may contain context that overlaps across different developments: do not merge because of shared background.
Return JSON {"sources":[{"source_id":"...","quality":"substantive","summary":"...","uncertainty":null}],"cards":[{"source_ids":["..."],"reason":"..."}],"related_events":[],"uncertainties":[]}."""
}
def run(graph,metadata,texts,variant,requester=request_analysis,endpoint="",model="",key="",max_calls=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    reviews=[];skipped=[];errors=[];calls=0
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_eligible_texts"});continue
        if calls>=max_calls:break
        calls+=1
        payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],"article_body":extracted[sid]["text"][:7000]} for sid in ids]}
        try:
            answer,usage=requester([{"role":"system","content":COMMON+"\n"+PROMPTS[variant]},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
            entries=answer.get("sources",[])
            if not isinstance(entries,list) or len(entries)!=len(ids) or {e.get("source_id") for e in entries if isinstance(e,dict)}!=set(ids):raise ValueError("source_ids_mismatch")
            for e in entries:
                if e.get("quality") not in ("substantive","insufficient"):raise ValueError("invalid_quality")
                if variant=="A":
                    if not isinstance(e.get("secondary"),list):raise ValueError("secondary_missing")
                    if e["quality"]=="substantive" and (not isinstance(e.get("primary"),str) or not e["primary"].strip()):raise ValueError("primary_missing")
                elif e["quality"]=="substantive" and (not isinstance(e.get("summary"),str) or not e["summary"].strip()):raise ValueError("summary_missing")
            eligible={e["source_id"] for e in entries if e["quality"]=="substantive"}
            cards=[];invalid=[];used=set()
            for card in answer.get("cards",[]):
                members=card.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=eligible or used.intersection(members):
                    invalid.append(card);continue
                cards.append({"source_ids":sorted(members),"reason":card.get("reason","")});used.update(members)
            reviews.append({"source_ids":ids,"sources":entries,"cards":cards,"invalid_groups":invalid,"standalone_source_ids":sorted(set(ids)-used),"related_events":answer.get("related_events",[]),"uncertainties":answer.get("uncertainties",[]),"usage":usage})
        except Exception as exc:errors.append({"source_ids":ids,"error_type":type(exc).__name__,"message":str(exc)[:250]})
    return {"variant":variant,"summary":{"contexts":len(reviews),"calls":calls,"errors":len(errors),"cards":sum(len(x["cards"]) for x in reviews),"sources":sum(len(x["sources"]) for x in reviews)},"reviews":reviews,"errors":errors,"skipped":skipped}
def main():
    p=argparse.ArgumentParser()
    for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
    p.add_argument("--variant",choices=["A","B"],required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--max-calls",type=int,default=20);a=p.parse_args()
    result=run(*(json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")),variant=a.variant,endpoint=os.environ["UBIK_LLM_ENDPOINT"],model=os.environ["UBIK_LLM_MODEL"],key=os.environ["UBIK_LLM_API_KEY"],max_calls=a.max_calls)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("AB_"+a.variant,json.dumps(result["summary"]))
if __name__=="__main__":main()
