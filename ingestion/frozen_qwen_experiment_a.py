"""Multi-statement extraction followed by within-call comparison. Frozen benchmark."""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM="""Read each source's actual article content; ignore navigation, recommendation headlines, sidebars, and unrelated links. Title is a clue, not evidence. If only a bulletin, video, or podcast listing without relevant story text is available, mark insufficient.
STAGE 1: Independently extract exactly ONE primary concrete statement per source, and up to FOUR secondary concrete statements. Each must be supported by the actual article text, identify who did or said what, and distinguish claims, reactions and decisions. If an article genuinely contains multiple unrelated main stories, mark quality='multi_story' and choose the clearest lead statement, without treating unrelated stories as its main news. For every statement return role ('primary' or 'secondary'), actor, kind ('action', 'statement', 'finding', 'opinion', or 'other'), statement. If no identifiable article content, return quality='insufficient' and zero statements. No invented facts.
STAGE 2: After extracting ALL sources, compare their ONE primary statement. Group only sources that report the same specific development. Related reactions, consequences, interviews and opinions stay distinct. Secondary statements may explain links but must not justify grouping. Return exactly JSON: {"sources":[{"source_id":"...","quality":"substantive|insufficient|multi_story","statements":[{"role":"primary|secondary","actor":"...","kind":"action|statement|finding|opinion|other","statement":"..."}]}],"cards":[{"source_ids":["..."],"reason":"..."}],"related_events":[{"source_ids":["..."],"relation":"..."}],"uncertainties":["..."]}. Every source exactly once."""
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
                if entry.get("quality") not in ("substantive","insufficient","multi_story"):raise ValueError("invalid_quality")
                if not isinstance(entry.get("statements"),list):raise ValueError("invalid_statements")
                primaries=[s for s in entry["statements"] if s.get("role")=="primary"]
                if len(primaries)!=(0 if entry["quality"]=="insufficient" else 1):raise ValueError("primary_statement_count")
                if len(entry["statements"])>5:raise ValueError("too_many_statements")
                for s in entry["statements"]:
                    if s.get("role") not in ("primary","secondary") or not isinstance(s.get("statement"),str) or not s["statement"].strip():raise ValueError("invalid_statement")
            eligible={e["source_id"] for e in entries if e["quality"]=="substantive" and any(s["role"]=="primary" for s in e["statements"])}
            cards=[];invalid=[];used=set()
            for card in answer.get("cards",[]):
                members=card.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=eligible or used.intersection(members):
                    invalid.append(card);continue
                cards.append({"source_ids":sorted(members),"reason":card.get("reason","")});used.update(members)
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
