"""Two lightweight cluster-level Qwen experiments on identical frozen sources."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
BASE="""You are a neutral news editor. Candidate sources were selected by topical similarity, NOT by verified event identity. It is equally correct to produce zero, one, or several cards. Do not optimize for either grouping or abstaining. Ignore unrelated headlines, navigation, boilerplate and recommended links. A title is a hypothesis to verify against the article body. Attribute statements and distinguish decisions from reactions and analysis. Never invent evidence. First represent EVERY source independently; only then compare their representations. A card requires the SAME concrete primary news development for ALL its members. Same topic, actor, cause, background, or reaction to another event does not establish identity. Leave different but related developments separate. Output EXACT JSON with sources and cards and related_events. Each source must appear exactly once in sources."""
PROMPTS={
"elements": BASE+"""
EXTRACTION: For every source, write a faithful 2-4 sentence summary. Identify ONE primary identity-defining development and 1-6 distinct elements with role identity|qualifier|context. Avoid splitting synonyms into different elements. Each element must be a supported concrete assertion, and count reflects distinct facts, NOT prose length. If multiple independent equally primary stories are present, quality=ambiguous and do not force one identity. If insufficient text, quality=insufficient.
COMPARISON: Group only when primary identity elements express the same specific development. Compare qualifiers for agreement, complementarity, or contradiction; context overlap cannot justify grouping. Different element counts are NOT a reason to separate. If a fact is primary in one source but only background in another, carefully check whether the sources' primary news differs. For each card give shared_development and matched_identity_elements; no need to create a card. Output JSON {"sources":[{"source_id":"...","quality":"substantive|insufficient|ambiguous","summary":"... or null","central_focus":"... or null","elements":[{"role":"identity|qualifier|context","claim":"..."}]}],"cards":[{"source_ids":["..."],"shared_development":"...","matched_identity_elements":["..."],"reason":"..."}],"related_events":[],"uncertainties":[]}.""",
"focus": BASE+"""
EXTRACTION: For each source write a faithful 2-4 sentence news summary. Then derive ONE central_focus stating the specific development that chiefly motivates publication; use the title as a hypothesis, not authority. Distinguish decisions, responses, editorials, and background. If the article is a generic bulletin or has multiple unrelated equally primary stories, mark ambiguous/insufficient and do not invent a focus.
COMPARISON: Examine all central_focus statements together. Propose groups only if every member primarily reports the SAME precise occurrence, decision, announcement, finding, or attributed reaction. Independently assess the whole group for coherence. Related but different events stay separate. Empty cards is valid. Output JSON {"sources":[{"source_id":"...","quality":"substantive|insufficient|ambiguous","summary":"... or null","central_focus":"... or null"}],"cards":[{"source_ids":["..."],"shared_development":"...","reason":"..."}],"related_events":[],"uncertainties":[]}."""
}
def run(graph,metadata,texts,endpoint,model,key,variant,max_contexts=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    reviews=[];errors=[];skipped=[];calls=0
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:
            skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_eligible"});continue
        if len(reviews)+len(errors)>=max_contexts:break
        payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],"article_body":extracted[sid]["text"][:7000]} for sid in ids]}
        answer=None;usage=[]
        for attempt in range(2):
            try:
                messages=[{"role":"system","content":PROMPTS[variant]},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}]
                if attempt:
                    messages[0]["content"]+=" CRITICAL: Return exactly one sources entry for EVERY provided ID, no omissions, even if quality is insufficient."
                answer,u=request_analysis(messages,endpoint,model,key,timeout=90);calls+=1;usage.append(u)
                entries=answer.get("sources",[])
                if not isinstance(entries,list) or len(entries)!=len(ids) or [e.get("source_id") for e in entries if isinstance(e,dict)]==[] or len({e.get("source_id") for e in entries if isinstance(e,dict)})!=len(ids) or {e.get("source_id") for e in entries if isinstance(e,dict)}!=set(ids):
                    raise ValueError("source_ids_mismatch")
                for e in entries:
                    if e.get("quality") not in ("substantive","insufficient","ambiguous"):raise ValueError("invalid_quality")
                    if e["quality"]=="substantive" and (not isinstance(e.get("summary"),str) or not isinstance(e.get("central_focus"),str)):raise ValueError("missing_representation")
                    if variant=="elements" and not isinstance(e.get("elements"),list):raise ValueError("missing_elements")
                eligible={e["source_id"] for e in entries if e["quality"]=="substantive"}
                cards=[];invalid=[];used=set()
                for c in answer.get("cards",[]):
                    members=c.get("source_ids",[])
                    if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=eligible or used.intersection(members):
                        invalid.append(c);continue
                    used.update(members);cards.append(c)
                reviews.append({"source_ids":ids,"sources":entries,"cards":cards,"invalid_groups":invalid,"standalone_source_ids":sorted(set(ids)-used),"related_events":answer.get("related_events",[]),"uncertainties":answer.get("uncertainties",[]),"usage":usage})
                break
            except Exception as exc:
                if attempt==1:errors.append({"source_ids":ids,"error":str(exc)[:250]})
    return {"variant":variant,"summary":{"contexts":len(reviews),"sources":sum(len(r["sources"]) for r in reviews),"cards":sum(len(r["cards"]) for r in reviews),"errors":len(errors),"calls":calls},"reviews":reviews,"errors":errors,"skipped":skipped}
def main():
    p=argparse.ArgumentParser()
    for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
    p.add_argument("--variant",choices=["elements","focus"],required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=run(*[json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")],endpoint=os.environ["UBIK_LLM_ENDPOINT"],model=os.environ["UBIK_LLM_MODEL"],key=os.environ["UBIK_LLM_API_KEY"],variant=a.variant)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("CLUSTER",json.dumps(out["summary"]))
if __name__=="__main__":main()
