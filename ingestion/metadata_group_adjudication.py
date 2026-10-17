"""Metadata-first LLM review of bounded candidate groups; no text scraping.

Review groups holistically and keep source-level provenance. Model decides event
identity, not graph connectivity. Never automatically publish card candidates.
"""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("You are an exacting news editor for Ubik. Compare titles, RSS descriptions, "
"dates and publishers ONLY. A CARD means the same specific news development "
"with nearly total overlap of the CENTRAL event, not a related response, reaction, "
"ongoing conflict, broad story, topic, or retrospective. Different reports of "
"one decision can share a card; a later reaction usually deserves another card. "
"Split distinct developments even when named entities coincide. "
"Do not mistake syndicated copies for independent corroboration. "
"Return JSON {cards:[{source_ids:[...],reason:string}],"
"related_distinct:[{source_ids:[...],reason:string}],"
"uncertain_source_ids:[...],notes:string}. Do not invent source IDs. "
"Prefer standalone sources to doubtful merges. The input has only metadata; "
"mark all accepted groups as PROVISIONAL and requiring review for high-impact use.")

def windows(context,edges,max_size=8):
    ids=context["source_ids"]
    # Neighbor-driven bounded windows preserve the highest-scoring edges.
    adj={x:[] for x in ids}
    for e in edges:
        if e["a"] in adj and e["b"] in adj:
            adj[e["a"]].append((e["score"],e["b"]))
            adj[e["b"]].append((e["score"],e["a"]))
    windows=[];seen=set()
    for sid in ids:
        window=tuple(sorted({sid,*[x for _,x in sorted(adj[sid],reverse=True)[:max_size-1]]}))
        if len(window)>=2 and window not in seen:
            seen.add(window);windows.append(window)
    return windows

def run(data,requester=request_analysis,endpoint="",model="",key="",max_calls=45):
    docs={s["id"]:s for s in data["sources"]}
    edges=data["candidate_pairs"];tasks=[];seen=set()
    for ctx in data["review_contexts"]:
        for ids in windows(ctx,edges):
            if ids not in seen:
                seen.add(ids);tasks.append(ids)
    # Highest-score candidate neighborhoods first, bounded budget.
    weight=lambda ids:max((e["score"] for e in edges if e["a"] in ids and e["b"] in ids),default=0)
    tasks.sort(key=weight,reverse=True)
    reviewed=[];proposals=[];errors=[]
    for ids in tasks[:max_calls]:
        payload={"sources":[docs[i] for i in ids],"candidate_edges":[e for e in edges if e["a"] in ids and e["b"] in ids]}
        try:
            response,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key)
            cards=response.get("cards",[])
            if not isinstance(cards,list):cards=[]
            accepted=[]
            for card in cards:
                members=card.get("source_ids",[])
                if isinstance(members,list) and len(members)==len(set(members)) and len(members)>=2 and set(members).issubset(ids):
                    accepted.append({"source_ids":sorted(members),"reason":card.get("reason",""),
                                     "status":"metadata_only_provisional"})
            reviewed.append({"source_ids":ids,"cards":accepted,"related_distinct":response.get("related_distinct",[]),
                "uncertain_source_ids":response.get("uncertain_source_ids",[]),"usage":usage})
            proposals+=accepted
        except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as e:
            errors.append({"source_ids":ids,"error_type":type(e).__name__})
    # Do not merge overlapping proposals automatically. Conflict requires review.
    unique={tuple(x["source_ids"]):x for x in proposals}
    conflicts=[]
    groups=list(unique)
    for i,a in enumerate(groups):
        for b in groups[i+1:]:
            if set(a)&set(b):conflicts.append({"a":list(a),"b":list(b),"shared":sorted(set(a)&set(b))})
    return {"summary":{"sources":len(docs),"candidate_edges":len(edges),"total_review_windows":len(tasks),
        "reviewed_windows":len(reviewed),"errors":len(errors),"proposed_distinct_groups":len(unique),
        "overlap_conflicts":len(conflicts),"unreviewed_windows":max(0,len(tasks)-max_calls)},
        "sources":data["sources"],"candidate_groups":list(unique.values()),"reviewed_windows":reviewed,
        "conflicts":conflicts,"errors":errors,"limitations":[
            "Metadata-only judgments are provisional, not evidence-grounded factual verification.",
            "Bounded LLM budget means not all windows may be reviewed.",
            "Overlapping groups remain separate until explicit editorial resolution.",
            "No automatic public card publication or nuclei creation."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--max-calls",type=int,default=45)
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM configuration")
    out=run(json.loads(a.input.read_text()),endpoint=endpoint,model=model,key=key,max_calls=max(1,min(60,a.max_calls)))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("Metadata group adjudication:",json.dumps(out["summary"]))
    for g in out["candidate_groups"][:20]:print("CANDIDATE",json.dumps(g,ensure_ascii=False))
if __name__=="__main__":main()
