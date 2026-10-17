"""Qwen whole-group semantic review of the 43-source frozen corpus.

Existing five topics and two nuclei are immutable context, not outcomes.
All 43 sources are considered for cards; pair edges are discovery hints only.
Qwen decides groups holistically, with a critical second pass and source passages.
"""
import argparse,collections,json,os,urllib.error
from pathlib import Path
from ingestion.cross_source_llm_adjudication import acquire,passages
from ingestion.llm_semantic_adapter import request_analysis

DISCOVERY=("You are Ubik's news editor. A CARD groups 2+ sources about ALMOST EXACTLY "
"the same specific development, not merely the same issue. A NUCLEUS can connect "
"partially overlapping, distinct developments. Existing topics and nuclei must remain. "
"Inspect the supplied substantial original passages and all candidate relations. "
"Find plausible cards of 2, 3 or more sources, without forcing merges. "
"Source IDs are globally unique. Return JSON {groups:[{source_ids:[...],"
"reason:string}],notes:string}. Only cite supplied source IDs. "
"An ambiguous match must remain separate. Do not invent events.")

REVIEW=("You are an independent critical editorial pass for Ubik, reviewing a proposed "
"whole-group card against the original source passages. Seek DISCONFIRMING evidence: "
"distinct central events, different dates, different actors, stages, or a broad theme "
"masquerading as one news event. Only accept if ALL included sources primarily "
"report the same specific development with almost total overlap in core facts. "
"An article can add compatible detail; an anthology/podcast may only count if its "
"relevant segment explicitly reports the same event. You may REMOVE sources or "
"reject the group, but never add unprovided sources. Preserve nuclei for partially "
"overlapping developments. Return JSON {accepted_source_ids:[...],"
"decision:string,reason:string,evidence_ids:{source_id:[passage_id,...]},"
"distinct_primary_developments:[string]}. Accept only >=2 sources.")

def run(pairs,grouping,strict,acquirer=acquire,requester=request_analysis,endpoint="",model="",key=""):
    sources=grouping["sources"];byid={s["id"]:s for s in sources}
    topic={sid:t["name"] for t in grouping["consolidated"]["topics"] for sid in t["source_ids"]}
    edges=[]
    for r in pairs["results"]:
        if r.get("status")!="analyzed":continue
        a=next((s["id"] for s in sources if s["url"]==r["left"]["url"]),None)
        b=next((s["id"] for s in sources if s["url"]==r["right"]["url"]),None)
        if a and b:edges.append({"a":a,"b":b,"relation":r.get("relation")})
    cache={};docs={}
    for s in sources:
        try:
            txt=acquirer(s["url"])
            ps=passages(txt[:8500],s["id"]+"P",max_passages=12)
            docs[s["id"]]={"id":s["id"],"title":s["title"],"topic":topic.get(s["id"]),
                "passages":ps,"text_available":bool(ps)}
        except (OSError,ValueError,PermissionError,TimeoutError,urllib.error.URLError):
            docs[s["id"]]={"id":s["id"],"title":s["title"],"topic":topic.get(s["id"]),
                "passages":[],"text_available":False}
    # Small topic-based batches plus a cross-topic pass. Cross-topic cards are allowed.
    batches=[]
    for t in grouping["consolidated"]["topics"]:
        ids=t["source_ids"]
        for i in range(0,len(ids),9):batches.append(ids[i:i+9])
    cross=[x["id"] for x in sources if x["id"] not in topic]
    if cross:batches.append(cross)
    # Supplement batches with all prior graph neighborhoods (including cross-topic edges).
    adj=collections.defaultdict(set)
    for e in edges:adj[e["a"]].add(e["b"]);adj[e["b"]].add(e["a"])
    for sid in sorted(adj):
        ids=[sid]+sorted(adj[sid])
        for i in range(0,len(ids),9):batches.append(ids[i:i+9])
    proposed=[];batch_errors=[]
    for i,ids in enumerate(batches):
        if len(ids)<2:continue
        payload={"sources":[docs[x] for x in ids],"prior_relations":[e for e in edges if e["a"] in ids and e["b"] in ids],
                 "prior_strict_cards":strict.get("cards",[]),"existing_nuclei":grouping["consolidated"].get("nucleus_proposals",[])}
        try:
            res,_=requester([{"role":"system","content":DISCOVERY},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key)
            for g in res.get("groups",[]):
                members=g.get("source_ids",[])
                if isinstance(members,list) and len(set(members))>=2 and set(members).issubset(ids):
                    proposed.append({"source_ids":sorted(set(members)),"reason":g.get("reason",""),"batch":i})
        except (OSError,ValueError,TypeError,KeyError,TimeoutError,urllib.error.URLError) as e:
            batch_errors.append({"batch":i,"type":type(e).__name__})
    # Explicitly carry over strict pair candidates for adversarial whole-group review.
    for card in strict.get("cards",[]):
        proposed.append({"source_ids":sorted(card["source_ids"]),"reason":"Prior strict pair candidate","batch":"prior"})
    unique={}
    for p in proposed:unique[tuple(p["source_ids"])]=p
    # Merge overlapping proposed groups into REVIEW contexts, never automatic card merges.
    graph=collections.defaultdict(set)
    for ids in unique:
        for a in ids:
            graph[a].update(set(ids)-{a})
    seen=set();contexts=[]
    for sid in sorted(graph):
        if sid in seen:continue
        todo=[sid];seen.add(sid);members=[]
        while todo:
            v=todo.pop();members.append(v)
            for n in graph[v]:
                if n not in seen:seen.add(n);todo.append(n)
        contexts.append(sorted(members))
    accepted=[];reviews=[];used=set()
    for i,members in enumerate(contexts):
        # Long chains are reviewed in bounded overlapping windows, not merged by transitivity.
        chunks=[members[j:j+9] for j in range(0,len(members),9)]
        for chunk in chunks:
            if len(chunk)<2:continue
            payload={"sources":[docs[x] for x in chunk],
                "candidate_groups":[v for k,v in unique.items() if set(k).intersection(chunk)],
                "existing_nuclei":grouping["consolidated"].get("nucleus_proposals",[])}
            try:
                result,_=requester([{"role":"system","content":REVIEW},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key)
                ids=result.get("accepted_source_ids",[])
                if not isinstance(ids,list):ids=[]
                valid=set(ids).issubset(chunk) and len(ids)==len(set(ids))
                evid=result.get("evidence_ids",{})
                if not isinstance(evid,dict):evid={}
                evidence_ok=valid and all(isinstance(evid.get(s),list) and bool(evid[s]) and
                    all(p in {v["id"] for v in docs[s]["passages"]} for p in evid[s]) for s in ids)
                approved=valid and evidence_ok and len(ids)>=2 and not used.intersection(ids)
                reviews.append({"context":chunk,"accepted_ids":ids,"decision":result.get("decision"),
                    "reason":result.get("reason"),"evidence_ok":evidence_ok,"approved":approved})
                if approved:
                    used.update(ids)
                    accepted.append({"source_ids":ids,"topics":sorted({topic.get(s,"Unassigned") for s in ids}),
                        "reason":result.get("reason"),"evidence_ids":{s:evid[s] for s in ids},
                        "status":"editorial_candidate"})
            except (OSError,ValueError,TypeError,KeyError,TimeoutError,urllib.error.URLError) as e:
                reviews.append({"context":chunk,"error":type(e).__name__})
    return {"summary":{"sources":len(sources),"sources_with_text":sum(d["text_available"] for d in docs.values()),
        "discovery_batches":len(batches),"discovery_errors":len(batch_errors),
        "proposed_groups":len(unique),"review_contexts":len(contexts),
        "accepted_card_candidates":len(accepted),
        "multi_source_cards":sum(len(x["source_ids"])>=3 for x in accepted),
        "sources_in_cards":len(used),"sources_standalone":len(sources)-len(used),
        "topics_preserved":len(grouping["consolidated"]["topics"]),
        "nuclei_preserved":len(grouping["consolidated"].get("nucleus_proposals",[]))},
        "sources":sources,"topics":grouping["consolidated"]["topics"],
        "nucleus_proposals":grouping["consolidated"].get("nucleus_proposals",[]),
        "source_tags":grouping["consolidated"].get("source_tags",{}),
        "proposed_groups":list(unique.values()),"cards":accepted,"reviews":reviews,
        "discovery_errors":batch_errors,
        "limitations":["Only 43 frozen sources; not the 984-source discovery corpus.",
        "Qwen discovery and critique are not independent models.",
        "Group review uses bounded contexts of at most nine sources; long chains may be split.",
        "No automatic publication."]}

def main():
    p=argparse.ArgumentParser()
    for name in ("pairs","grouping","strict"):p.add_argument(name,type=Path)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM credentials")
    out=run(*(json.loads(getattr(a,n).read_text()) for n in ("pairs","grouping","strict")),
        endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("Whole-group cards:",json.dumps(out["summary"]))
    for c in out["cards"]:print("CARD",json.dumps(c,ensure_ascii=False))
if __name__=="__main__":main()
