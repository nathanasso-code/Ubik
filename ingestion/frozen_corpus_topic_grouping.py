"""Conservative topic/tag/nucleus proposal from ALL sources in frozen LLM pairs.

Pair edges are retrieval signals, never automatic card merges or nucleus publication.
"""
import argparse,collections,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("You organize a curated news information platform. Input contains ALL distinct source titles and "
"previously reviewed pair relationships. Make a compact set of broad, coherent TOPIC proposals that group "
"multiple distinct news developments, not cards. Preserve source IDs. "
"A TOPIC is a persistent broad information area, not a category per source; use a small number. "
"TAGS are specific, searchable metadata attached to sources and reusable across topics. "
"A NUCLEUS is rare, narrowly scoped, persistent issue suitable for community discussion across several "
"distinct news items. Suggest nuclei only if clearly warranted by multiple distinct developments; "
"do not invent one for each topic, group or card. "
"Relations related_separate_developments and same_persistent_issue are signals for cross-card grouping, "
"not proof of same event. Topic-only pairs can share a topic without sharing a nucleus. "
"Do not force unrelated documents into a topic. Never claim facts from titles alone. "
"Return JSON with keys topics (array of {name, source_ids, tags}), "
"nucleus_proposals (array of {title, topic_name, source_ids, justification}), "
"unassigned_source_ids (array), source_tags (object mapping source ID to 2-6 tags), "
"notes (brief). Every input source ID must appear in exactly one topic or unassigned; "
"no unknown IDs. Use existing broad topic names where natural: Artificial intelligence, "
"Ukraine and international relations, Science and technology, Environment and public health, "
"Politics and society. A source may have tags across multiple domains but one primary topic.")

def prepare(report):
    docs={};pairs=[]
    for r in report["results"]:
        for side in ("left","right"):
            s=r[side];docs[s["url"]]={"title":s["title"],"url":s["url"],"publisher":s.get("publisher")}
    indexed={url:f"D{i+1}" for i,url in enumerate(sorted(docs))}
    sources=[{"id":indexed[url],**docs[url]} for url in sorted(docs)]
    for r in report["results"]:
        if r.get("status")!="analyzed":continue
        pairs.append({"a":indexed[r["left"]["url"]],"b":indexed[r["right"]["url"]],
            "relation":r.get("relation"),"reason":r.get("reason","")[:240]})
    return sources,pairs

def validate(proposal,sources):
    ids={s["id"] for s in sources};topics=proposal.get("topics",[])
    if not isinstance(topics,list):return False,"topics_not_list"
    assigned=[]
    for t in topics:
        if not isinstance(t,dict) or not isinstance(t.get("source_ids"),list):return False,"invalid_topic"
        assigned+=t["source_ids"]
    unassigned=proposal.get("unassigned_source_ids",[])
    if not isinstance(unassigned,list):return False,"invalid_unassigned"
    assigned+=unassigned
    if len(assigned)!=len(set(assigned)) or set(assigned)!=ids:return False,"incomplete_or_duplicate_assignment"
    for n in proposal.get("nucleus_proposals",[]):
        if not isinstance(n,dict) or not set(n.get("source_ids",[])).issubset(ids):return False,"invalid_nucleus"
    return True,None

def normalize_assignment(proposal,sources):
    """Repair only bookkeeping: first topic wins; absent IDs remain unassigned.

    No semantic membership is invented, and repairs are explicitly reported.
    """
    ids={s["id"] for s in sources};seen=set();repairs=[]
    for topic in proposal.get("topics",[]):
        unique=[]
        for sid in topic.get("source_ids",[]):
            if sid not in ids or sid in seen:
                repairs.append({"id":sid,"action":"remove_duplicate_or_unknown_topic_assignment"})
            else:seen.add(sid);unique.append(sid)
        topic["source_ids"]=unique
    unassigned=[]
    for sid in proposal.get("unassigned_source_ids",[]):
        if sid not in ids or sid in seen:
            repairs.append({"id":sid,"action":"remove_duplicate_or_unknown_unassigned"})
        else:seen.add(sid);unassigned.append(sid)
    for sid in sorted(ids-seen):
        unassigned.append(sid)
        repairs.append({"id":sid,"action":"missing_from_llm_output_left_unassigned"})
    proposal["unassigned_source_ids"]=unassigned
    return repairs

def run(report,requester=request_analysis,endpoint="",model="",key=""):
    sources,pairs=prepare(report)
    # Two-stage batching avoids truncated JSON for 50+ documents and allows coherent global consolidation.
    batches=[sources[i:i+20] for i in range(0,len(sources),20)]
    drafts=[];errors=[]
    for i,batch in enumerate(batches):
        local={s["id"] for s in batch}
        local_pairs=[p for p in pairs if p["a"] in local and p["b"] in local]
        try:
            proposal,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps({"sources":batch,"relationships":local_pairs,
                  "instruction":"Draft topics and tags for this batch. Keep nuclei rare."},ensure_ascii=False)}],endpoint,model,key)
            repairs=normalize_assignment(proposal,batch)
            valid,error=validate(proposal,batch)
            drafts.append({"batch":i+1,"source_count":len(batch),"valid":valid,"validation_error":error,
                           "proposal":proposal,"usage":usage,"assignment_repairs":repairs})
        except (ValueError,KeyError,TypeError,OSError,TimeoutError,urllib.error.URLError) as e:
            errors.append({"batch":i+1,"error_type":type(e).__name__,"http_status":getattr(e,"code",None)})
    if errors or not all(x["valid"] for x in drafts):
        return {"schema_version":1,"summary":{"sources":len(sources),"pairs":len(pairs),
            "draft_batches":len(drafts),"errors":len(errors),"validated":False},
            "drafts":drafts,"errors":errors,"sources":sources}
    # Consolidation includes every source, all pairwise signals and draft decisions.
    compact=[{"batch":d["batch"],"topics":d["proposal"].get("topics",[]),
              "nucleus_proposals":d["proposal"].get("nucleus_proposals",[]),
              "unassigned_source_ids":d["proposal"].get("unassigned_source_ids",[]),
              "source_tags":d["proposal"].get("source_tags",{})} for d in drafts]
    try:
        final,usage=requester([{"role":"system","content":SYSTEM},
            {"role":"user","content":json.dumps({"sources":sources,"relationships":pairs,
              "batch_drafts":compact,
              "instruction":"GLOBAL consolidation: reconcile synonyms and merge overfragmented topic groups; all sources exactly once. Preserve useful topic-only and related-development relationships. Be conservative with nuclei."},ensure_ascii=False)}],endpoint,model,key)
        final_repairs=normalize_assignment(final,sources)
        valid,error=validate(final,sources)
        return {"schema_version":1,"model":model,"summary":{"sources":len(sources),"pairs":len(pairs),
            "draft_batches":len(drafts),"errors":0,"validated":valid,
            "topics":len(final.get("topics",[])) if valid else None,
            "nuclei_proposed":len(final.get("nucleus_proposals",[])) if valid else None,
            "unassigned":len(final.get("unassigned_source_ids",[])) if valid else None},
            "sources":sources,"relationships":pairs,"consolidated":final,"validation_error":error,
            "usage":usage,"drafts":drafts,"global_assignment_repairs":final_repairs,
            "limitations":["Same frozen 54 reviewed pairs, with every distinct source included.",
             "No original texts in this stage; grouping relies on titles and earlier text-grounded pair reasons.",
             "Cross-batch pairs enter global consolidation; missing pair edges are not proof of unrelatedness.",
             "Topic and nucleus proposals are not editorially validated or published.",
             "Only proposed cards from separate full-text group review may merge same-event sources."]}
    except (ValueError,KeyError,TypeError,OSError,TimeoutError,urllib.error.URLError) as e:
        return {"schema_version":1,"summary":{"sources":len(sources),"pairs":len(pairs),"validated":False,
            "errors":1},"error_type":type(e).__name__,"sources":sources,"drafts":drafts}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not (endpoint and model and key):p.error("Missing LLM credentials")
    result=run(json.loads(a.input.read_text()),endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Frozen full-corpus topic grouping:",json.dumps(result["summary"]))
    if result.get("consolidated"):
        for t in result["consolidated"].get("topics",[]):
            print("TOPIC",t.get("name"),"sources",len(t.get("source_ids",[])),"tags",t.get("tags"))
        for n in result["consolidated"].get("nucleus_proposals",[]):
            print("NUCLEUS PROPOSAL",n.get("title"),"sources",len(n.get("source_ids",[])))
if __name__=="__main__":main()
