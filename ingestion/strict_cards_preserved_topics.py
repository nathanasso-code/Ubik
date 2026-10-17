"""Strict multi-source card candidates preserving frozen global topic assignments.

Every one of 54 previously analyzed relationships is re-adjudicated with original
substantial text; only high-overlap, near-identical news is a card edge.
Multi-source groups are derived from mutually compatible (clique) edges, never
mere transitive connected components. All 43 sources stay visible in topics.
"""
import argparse,collections,json,os,urllib.error
from pathlib import Path
from ingestion.cross_source_llm_adjudication import acquire,passages
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("You are a strict Ubik editor. Decide whether TWO original news sources report ALMOST "
"THE EXACT SAME specific news development, rather than similar issues, parallel events, "
"consecutive stages, related policy, or different angles with materially distinct primary facts. "
"A card can contain 2 or more sources, but requires very high factual overlap in the MAIN development: "
"same actors, same core action, same location and compatible event time. "
"Related but different events should be separate cards or sources in the SAME NUCLEUS, "
"and may remain in the same TOPIC. Never merge on topical similarity. "
"Generic radio/podcast titles must be judged on their actual passages. "
"Return JSON object {same_near_identical_news: boolean, "
"reason: string, evidence_a_id: string, evidence_b_id: string, "
"shared_primary_facts: [string], materially_different_primary_facts: [string], "
"tags: [string]}. Be conservative; when in doubt, false.")

def run(relationships,grouping,acquirer=acquire,requester=request_analysis,endpoint="",model="",key=""):
    sources=grouping["sources"];byid={s["id"]:s for s in sources}
    topic_of={}
    for t in grouping["consolidated"]["topics"]:
        for sid in t["source_ids"]:topic_of[sid]=t["name"]
    byurl={s["url"]:s["id"] for s in sources}
    cache={};reviews=[];edges=set()
    for i,pair in enumerate(relationships["results"]):
        if pair.get("status")!="analyzed":continue
        aid=byurl.get(pair["left"]["url"]);bid=byurl.get(pair["right"]["url"])
        if not aid or not bid or aid==bid:continue
        fetched=[]
        for sid in (aid,bid):
            url=byid[sid]["url"]
            if url not in cache:
                try:cache[url]={"text":acquirer(url)}
                except (OSError,ValueError,PermissionError,TimeoutError,urllib.error.URLError) as e:cache[url]={"error":type(e).__name__}
            fetched.append(cache[url])
        base={"pair_index":i,"a":aid,"b":bid,"prior_relation":pair.get("relation"),
              "topic_a":topic_of.get(aid),"topic_b":topic_of.get(bid)}
        if any("text" not in v for v in fetched):
            reviews.append({**base,"status":"insufficient_text"});continue
        pa=passages(fetched[0]["text"][:8500],"AP",max_passages=18)
        pb=passages(fetched[1]["text"][:8500],"BP",max_passages=18)
        try:
            verdict,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps({"a":{"title":byid[aid]["title"],"passages":pa},
                    "b":{"title":byid[bid]["title"],"passages":pb},
                    "prior_relation_for_context_only":pair.get("relation")},ensure_ascii=False)}],
                    endpoint,model,key)
            valid=verdict.get("evidence_a_id") in {x["id"] for x in pa} and verdict.get("evidence_b_id") in {x["id"] for x in pb}
            same=verdict.get("same_near_identical_news") is True and valid
            if same:edges.add(tuple(sorted((aid,bid))))
            reviews.append({**base,"status":"reviewed","same_near_identical_news":same,
                "passage_ids_valid":valid,"raw_model_same":verdict.get("same_near_identical_news"),
                "raw_evidence_a_id":verdict.get("evidence_a_id"),"raw_evidence_b_id":verdict.get("evidence_b_id"),
                "expected_evidence_a_ids":[x["id"] for x in pa],
                "expected_evidence_b_ids":[x["id"] for x in pb],
                "reason":str(verdict.get("reason",""))[:700],
                "shared_primary_facts":verdict.get("shared_primary_facts",[]),
                "materially_different_primary_facts":verdict.get("materially_different_primary_facts",[]),
                "tags":verdict.get("tags",[]),"usage":usage})
        except (OSError,ValueError,TypeError,KeyError,TimeoutError,urllib.error.URLError) as e:
            reviews.append({**base,"status":"error","error_type":type(e).__name__})
    # All members of a multi-source card must have a validated direct edge with each other.
    # Missing edges are not inferred from a connected path. Disjoint greedy cliques,
    # sorted by size, avoid assigning the same source to multiple proposed cards.
    nodes=sorted({x for edge in edges for x in edge})
    cliques=[]
    def expand(chosen,candidates):
        if len(chosen)>=2:cliques.append(tuple(chosen))
        for i,v in enumerate(candidates):
            expand(chosen+[v],[w for w in candidates[i+1:] if tuple(sorted((v,w))) in edges])
    expand([],nodes)
    cliques.sort(key=lambda c:(-len(c),c))
    cards=[];used=set()
    for clique in cliques:
        if used.intersection(clique):continue
        used.update(clique)
        topics=sorted({topic_of.get(sid,"Unassigned") for sid in clique})
        cards.append({"source_ids":list(clique),"titles":[byid[sid]["title"] for sid in clique],
            "topics":topics,"status":"candidate_needs_editorial_review"})
    return {"schema_version":1,"summary":{"sources":len(sources),"prior_pairs":len(relationships["results"]),
        "pairs_rechecked":len(reviews),"pairs_with_text":sum(x["status"]=="reviewed" for x in reviews),
        "near_identical_pairs":len(edges),"candidate_cards":len(cards),
        "cards_with_three_or_more_sources":sum(len(c["source_ids"])>=3 for c in cards),
        "sources_in_cards":len(used),"sources_outside_cards":len(sources)-len(used),
        "topics_preserved":len(grouping["consolidated"]["topics"])},
        "topics":grouping["consolidated"]["topics"],
        "nucleus_proposals":grouping["consolidated"].get("nucleus_proposals",[]),
        "source_tags":grouping["consolidated"].get("source_tags",{}),
        "sources":sources,"cards":cards,"pair_reviews":reviews,
        "limitations":["Only previously retrieved 54 pairs evaluated, not every possible pair of 43 sources.",
          "Strict clique grouping avoids transitive false merges but may miss valid multi-source cards.",
          "Topic and nucleus proposals preserved unchanged; not published.",
          "Original text acquired at runtime and not persisted; no independent editorial gold standard."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("pairs",type=Path);p.add_argument("grouping",type=Path)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not (endpoint and model and key):p.error("Missing LLM credentials")
    result=run(json.loads(a.pairs.read_text()),json.loads(a.grouping.read_text()),
        endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Strict cards with preserved topics:",json.dumps(result["summary"]))
    for c in result["cards"]:print("CARD",json.dumps(c,ensure_ascii=False))
if __name__=="__main__":main()
