"""Multi-statement extraction followed by within-call comparison. Frozen benchmark."""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM="""STAGE 1: Independently read each supplied article and produce a faithful 2-4 sentence overall news summary. The article's own text is authoritative; title only a clue. Ignore navigation, related links, sidebars, boilerplate. Preserve attribution and distinguish decisions, reactions, opinions, claims and consequences. If there is no meaningful article body (including generic video/bulletin listings), mark insufficient and summary=null. Do not invent.
STAGE 2: Only after ALL independent summaries, for EACH source extract ONE concise central_focus sentence identifying the specific development the article itself foregrounds. This focus must be supported by that source's summary and must NOT be a general topic label. Retain secondary context in the summary but not in central_focus. If insufficient, central_focus=null.
STAGE 3: Compare central_focus sentences rather than overall topical similarity. Before accepting any group, provide a concrete shared_development sentence expressing the SAME specific decision, action, announcement, finding or attributed reaction centrally reported by EVERY group member. If no such precise shared development exists, do NOT group. Related but distinct reactions, consequences, interviews and editorials remain separate, with optional related_events links. Reject broad statements such as 'Russia sanctions developments' as group identities. Return exactly JSON {"sources":[{"source_id":"...","quality":"substantive|insufficient","summary":"... or null","central_focus":"... or null"}],"cards":[{"source_ids":["..."],"shared_development":"...","reason":"..."}],"related_events":[{"source_ids":["..."],"relation":"..."}],"uncertainties":["..."]}. Every source exactly once."""
def run(graph,metadata,texts,requester=request_analysis,endpoint="",model="",key="",max_calls=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    reviews=[];skipped=[];errors=[];calls=0
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:
            skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_substantial_texts"});continue
        if calls>=max_calls:break
        calls+=1
        payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],"article_body":extracted[sid]["text"][:7000]} for sid in ids]}
        try:
            answer,usage=requester([{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
            entries=answer.get("sources",[])
            if not isinstance(entries,list) or len(entries)!=len(ids) or {e.get("source_id") for e in entries if isinstance(e,dict)}!=set(ids):raise ValueError("source_ids_mismatch")
            for entry in entries:
                if entry.get("quality") not in ("substantive","insufficient"):raise ValueError("invalid_quality")
                if entry["quality"]=="substantive" and (not isinstance(entry.get("summary"),str) or not isinstance(entry.get("central_focus"),str)):raise ValueError("missing_summary_or_focus")
            eligible={e["source_id"] for e in entries if e["quality"]=="substantive" and e.get("summary") and e.get("central_focus")}
            cards=[];invalid=[];used=set()
            for card in answer.get("cards",[]):
                members=card.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=eligible or used.intersection(members):
                    invalid.append(card);continue
                cards.append({"source_ids":sorted(members),"shared_development":card.get("shared_development",""),"reason":card.get("reason","")});used.update(members)
            reviews.append({"source_ids":ids,"sources":entries,"cards":cards,"invalid_groups":invalid,"standalone_source_ids":sorted(set(ids)-used),"related_events":answer.get("related_events",[]),"uncertainties":answer.get("uncertainties",[]),"usage":usage})
        except Exception as exc:errors.append({"source_ids":ids,"error":str(exc)[:250]})
    return {"summary":{"contexts":len(reviews),"calls":calls,"errors":len(errors),"cards":sum(len(x["cards"]) for x in reviews),"sources":sum(len(x["sources"]) for x in reviews)},"reviews":reviews,"errors":errors,"skipped":skipped}
def main():
    p=argparse.ArgumentParser()
    for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
    p.add_argument("--output",required=True,type=Path);p.add_argument("--max-calls",type=int,default=20);a=p.parse_args()
    result=run(*(json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")),endpoint=os.environ["UBIK_LLM_ENDPOINT"],model=os.environ["UBIK_LLM_MODEL"],key=os.environ["UBIK_LLM_API_KEY"],max_calls=a.max_calls)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("MULTI_STATEMENT",json.dumps(result["summary"]))
if __name__=="__main__":main()
