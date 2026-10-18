"""Controlled pairwise identity adjudication on the frozen Ubik benchmark."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

EXTRACT="""Read EACH source independently. Produce a faithful 2-4 sentence summary, then ONE central_focus: the specific informational development that chiefly motivates publication. Treat title as a hypothesis verified against the body. Separate the primary event from reactions, commentary, background, and other events. Ignore page boilerplate. A bulletin or listing with no actual article narrative is insufficient. If multiple autonomous stories are equally primary, mark ambiguous. Return JSON {"sources":[{"source_id":"...","quality":"substantive|insufficient|ambiguous","summary":"... or null","central_focus":"... or null","uncertainty":"... or null"}]}. Every supplied source exactly once."""
PAIR="""You are a neutral editor assessing whether TWO independently extracted central news developments are identical. No preference for SAME or DISTINCT: either is equally useful. SAME means both sources primarily report the SAME specific occurrence/decision/statement/finding, even if wording differs. DISTINCT_RELATED means shared people, topic, cause, background, or coverage but DIFFERENT primary developments. UNCERTAIN means insufficient information to establish either conclusion. Do not infer SAME merely from matching names or surrounding context. Compare only supplied summaries and central_focus; do not invent evidence. Return JSON {"decision":"SAME|DISTINCT_RELATED|UNCERTAIN","shared_development":"... or null","reason":"..."}. An exact identity must be expressible without broadening beyond either source's main event."""
def call(system,payload,endpoint,model,key):
    answer,usage=request_analysis([{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
    return answer,usage
def run(graph,metadata,texts,endpoint,model,key,max_contexts=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    results=[];errors=[];skipped=[];calls=0
    for case in metadata["reviews"]:
        ids=[sid for sid in case["source_ids"] if sid in extracted]
        if len(ids)<2:
            skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_eligible"});continue
        if len(results)+len(errors)>=max_contexts:break
        payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],"article_body":extracted[sid]["text"][:7000]} for sid in ids]}
        try:
            # One-source-at-a-time extraction prevents missing IDs and cross-source leakage.
            entries=[];usage=[]
            for item in payload["sources"]:
                sid=item["id"]
                a,u=call(EXTRACT,{"sources":[item]},endpoint,model,key);calls+=1
                es=a.get("sources",[])
                if len(es)!=1 or es[0].get("source_id")!=sid:raise ValueError("source_extraction_mismatch:"+sid)
                e=es[0]
                if e.get("quality") not in ("substantive","insufficient","ambiguous"):raise ValueError("invalid_quality:"+sid)
                if e["quality"]=="substantive" and (not isinstance(e.get("summary"),str) or not isinstance(e.get("central_focus"),str)):raise ValueError("missing_summary_or_focus:"+sid)
                entries.append(e);usage.append({"phase":"extract","source_id":sid,"usage":u})
            eligible=[e for e in entries if e["quality"]=="substantive"]
            decisions=[];pair_errors=[]
            for i,a in enumerate(eligible):
                for b in eligible[i+1:]:
                    try:
                        response,u=call(PAIR,{"a":a,"b":b},endpoint,model,key);calls+=1
                        d=response.get("decision")
                        if d not in ("SAME","DISTINCT_RELATED","UNCERTAIN"):raise ValueError("invalid_pair_decision")
                        decisions.append({"a":a["source_id"],"b":b["source_id"],"decision":d,"shared_development":response.get("shared_development"),"reason":response.get("reason"),"usage":u})
                    except Exception as exc:
                        pair_errors.append({"a":a["source_id"],"b":b["source_id"],"error":str(exc)[:150]})
            # Strict complete-link grouping: a group is accepted only if every pair is SAME.
            same={frozenset((p["a"],p["b"])) for p in decisions if p["decision"]=="SAME"}
            clusters=[{e["source_id"]} for e in eligible]
            while True:
                candidate=None
                for i in range(len(clusters)):
                    for j in range(i+1,len(clusters)):
                        if all(frozenset((x,y)) in same for x in clusters[i] for y in clusters[j]):
                            score=len(clusters[i])+len(clusters[j])
                            if candidate is None or score>candidate[0]:candidate=(score,i,j)
                if candidate is None:break
                _,i,j=candidate;clusters[i]|=clusters[j];clusters.pop(j)
            cards=[{"source_ids":sorted(c)} for c in clusters if len(c)>1]
            used={sid for c in cards for sid in c["source_ids"]}
            results.append({"source_ids":ids,"sources":entries,"pair_decisions":decisions,"pair_errors":pair_errors,"cards":cards,"standalone_source_ids":sorted(set(ids)-used),"usage":usage})
        except Exception as exc:
            errors.append({"source_ids":ids,"error":str(exc)[:300]})
    return {"summary":{"contexts":len(results),"sources":sum(len(r["sources"]) for r in results),"cards":sum(len(r["cards"]) for r in results),"calls":calls,"errors":len(errors),"pair_errors":sum(len(r["pair_errors"]) for r in results)},"reviews":results,"errors":errors,"skipped":skipped}
def main():
    p=argparse.ArgumentParser()
    for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=run(*[json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")],endpoint=os.environ["UBIK_LLM_ENDPOINT"],model=os.environ["UBIK_LLM_MODEL"],key=os.environ["UBIK_LLM_API_KEY"])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("PAIRWISE_IDENTITY",json.dumps(out["summary"]))
if __name__=="__main__":main()
