"""Cached per-source information atoms and cluster-level identity adjudication.

Experiment only: outputs review proposals, never publishes merges.
"""
import argparse,json,os,time
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

EXTRACT="""Independently read this one news source. Ignore navigation and related links. Return JSON {"source_id":"...","quality":"substantive|insufficient|ambiguous","summary":"2-4 faithful sentences or null","primary":{"actor":"...","action":"...","object":"...","event_type":"decision|reaction|report|finding|event|analysis|other","reference":"specific identifying detail"},"elements":[{"role":"identity|qualifier|context","claim":"distinct supported factual assertion"}]}. 1-6 elements. Primary is the development chiefly motivating publication, not a contextual event mentioned in the article. If this is primarily a reaction to a decision, actor/action describe the REACTION, not the underlying decision. Mark ambiguous if multiple independent primary developments. No invented facts."""
GROUP="""Neutral news identity editor. You receive independent structured representations, NOT original article bodies. No preference for grouping or splitting. Propose groups only when every member primarily reports the SAME specific occurrence/decision/reaction/finding. Related event, shared object, actors, cause or context do not justify merging. A decision and a reaction to it are DIFFERENT developments even if they mention the same event. Different numbers of details are allowed. Return JSON {"cards":[{"source_ids":["..."],"shared_development":"precise identity sentence","reason":"..."}],"relations":[{"source_ids":["..."],"relation":"REACTION_TO|FOLLOW_UP|SHARED_CONTEXT|UNCERTAIN","reason":"..."}],"uncertainties":[]}. Empty cards is valid. Use only supplied source IDs."""
CHECK="""You are an independent skeptical reviewer of ONE proposed news card. Compare each member's PRIMARY development against the proposed shared_development. Reject when a source merely cites that development as context, reports a reaction to it, or primarily covers a distinct event. Do not demand equal numbers of details. Return JSON {"accept":true,"reason":"...","mismatched_source_ids":[]}. Be precise and neutral."""
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    tmp.replace(path)
def call(prompt,data,endpoint,model,key):
    return request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(data,ensure_ascii=False)}],endpoint,model,key,timeout=90)
def usage_add(total,usage):
    for k in ("prompt_tokens","completion_tokens","total_tokens"):
        if isinstance(usage.get(k),int):total[k]=total.get(k,0)+usage[k]
    if isinstance(usage.get("cost"),(int,float)):total["reported_cost_usd"]=total.get("reported_cost_usd",0)+usage["cost"]
def main():
    p=argparse.ArgumentParser()
    for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--cache",type=Path,required=True)
    a=p.parse_args()
    graph=json.loads(a.graph.read_text());metadata=json.loads(a.metadata.read_text());texts=json.loads(a.texts.read_text())
    byid={s["id"]:s for s in graph["sources"]}
    source_text={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    endpoint=os.environ["UBIK_LLM_ENDPOINT"];model=os.environ["UBIK_LLM_MODEL"];key=os.environ["UBIK_LLM_API_KEY"]
    cache=json.loads(a.cache.read_text()) if a.cache.exists() else {}
    out={"schema_version":1,"model":model,"sources":{},"reviews":[],"errors":[],"usage":{},"calls":0,"limitations":["LLM identity verification is not ground truth.","Only first 7000 characters per source used.","Outputs require human review before publishing."]}
    def request(prompt,data):
        answer,u=call(prompt,data,endpoint,model,key)
        out["calls"]+=1;usage_add(out["usage"],u)
        return answer
    cases=[c for c in metadata["reviews"] if len([sid for sid in c["source_ids"] if sid in source_text])>=2]
    all_ids=list(dict.fromkeys(sid for c in cases for sid in c["source_ids"] if sid in source_text))
    for sid in all_ids:
        if sid in cache and cache[sid].get("source_id")==sid and isinstance(cache[sid].get("elements"),list):
            out["sources"][sid]=cache[sid];continue
        s=byid[sid];t=source_text[sid]["text"]
        for attempt in range(2):
            try:
                answer=request(EXTRACT,{"id":sid,"title":s["title"],"url":s["url"],"body":t[:7000]})
                if answer.get("source_id")!=sid or answer.get("quality") not in ("substantive","insufficient","ambiguous") or not isinstance(answer.get("elements"),list):raise ValueError("invalid_extraction")
                primary=answer.get("primary")
                if answer["quality"]=="substantive" and (not isinstance(primary,dict) or not all(primary.get(k) for k in ("actor","action","object","event_type"))):raise ValueError("invalid_primary")
                cache[sid]=answer;out["sources"][sid]=answer;write(a.cache,cache);write(a.output,out)
                break
            except Exception as exc:
                if attempt==1:
                    out["errors"].append({"phase":"extraction","source_id":sid,"error":str(exc)[:180]});write(a.output,out)
    for case in cases:
        ids=[sid for sid in case["source_ids"] if sid in out["sources"]]
        eligible=[out["sources"][sid] for sid in ids if out["sources"][sid]["quality"]=="substantive"]
        review={"source_ids":ids,"cards":[],"rejected_cards":[],"relations":[],"standalone_source_ids":ids}
        if len(eligible)<2:
            out["reviews"].append(review);write(a.output,out);continue
        try:
            proposal=request(GROUP,{"sources":eligible})
            review["relations"]=proposal.get("relations",[])
            used=set()
            for card in proposal.get("cards",[]):
                members=card.get("source_ids",[])
                if len(members)<2 or len(set(members))!=len(members) or not set(members)<={x["source_id"] for x in eligible} or set(members)&used:
                    review["rejected_cards"].append({"card":card,"reason":"invalid_membership"});continue
                representations=[out["sources"][sid] for sid in members]
                # Cheap deterministic warning: incompatible primary event types merit semantic verification.
                types={r["primary"].get("event_type") for r in representations}
                warning="different_event_types" if len(types)>1 else None
                try:
                    verdict=request(CHECK,{"card":card,"sources":representations,"warning":warning})
                    if verdict.get("accept") is True and not verdict.get("mismatched_source_ids"):
                        review["cards"].append({"card":card,"verification":verdict});used.update(members)
                    else:review["rejected_cards"].append({"card":card,"verification":verdict})
                except Exception as exc:
                    review["rejected_cards"].append({"card":card,"reason":"verification_error","error":str(exc)[:180]})
            review["standalone_source_ids"]=[sid for sid in ids if sid not in used]
        except Exception as exc:
            out["errors"].append({"phase":"cluster","source_ids":ids,"error":str(exc)[:180]})
        out["reviews"].append(review);write(a.output,out)
    out["summary"]={"eligible_sources":len(all_ids),"extracted_sources":len(out["sources"]),"contexts":len(out["reviews"]),"accepted_cards":sum(len(x["cards"]) for x in out["reviews"]),"rejected_cards":sum(len(x["rejected_cards"]) for x in out["reviews"]),"errors":len(out["errors"]),"calls":out["calls"]}
    write(a.output,out);print(json.dumps(out["summary"]))
if __name__=="__main__":main()
