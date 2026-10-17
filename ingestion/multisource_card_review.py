"""Second-pass multi-source card review on the frozen 54-pair Qwen report.

No transitive merge is accepted without a whole-group LLM check and substantial
source text. Related developments and topic-only edges never imply card identity.
"""
import argparse,collections,json,os,urllib.error
from pathlib import Path
from ingestion.cross_source_llm_adjudication import acquire,passages,provider_error_code
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("You are the second-pass editor of Ubik, an evidence-grounded information platform. "
"An epistemic CARD is a single news item or specific development, possibly with THREE OR MORE sources. "
"A TOPIC is a broad curated area; TAGS are short descriptive searchable terms. "
"A NUCLEUS is a rare persistent scoped issue connecting multiple cards and discussion; never create one automatically. "
"Given candidate sources and substantial original passages, identify which source IDs truly describe ONE same news development. "
"Do not force all sources into one card; exclude sources with different events, or insufficient evidence. "
"Check actors, place, dates, action and temporal sequence. Compatible complementary details are allowed. "
"Generic program/roundup titles are NOT evidence of same development. "
"Return JSON object with: included_ids (array of source IDs), excluded_ids (array of source IDs), "
"decision (card_candidate or split_or_uncertain), card_title (short, cautious), "
"reason (specific identifying facts and uncertainty), tags (3-7 specific short non-hashtag labels), "
"topic_suggestion (existing broad topic name or null), evidence_ids (object mapping each included source ID to an existing passage ID). "
"Do not invent passage IDs or event details. Do not produce a nucleus.")

def components(rows):
    edges=[r for r in rows if r.get("status")=="analyzed" and r.get("relation")=="same_news_development" and r.get("accepted_for_review")]
    graph=collections.defaultdict(set);source={}
    for r in edges:
        a,b=r["left"],r["right"]
        source[a["url"]]=a;source[b["url"]]=b
        graph[a["url"]].add(b["url"]);graph[b["url"]].add(a["url"])
    found=[];seen=set()
    for url in sorted(graph):
        if url in seen:continue
        todo=[url];seen.add(url);group=[]
        while todo:
            u=todo.pop();group.append(source[u])
            for v in graph[u]:
                if v not in seen:seen.add(v);todo.append(v)
        found.append(sorted(group,key=lambda x:x["url"]))
    return sorted(found,key=lambda g:(-len(g),g[0]["url"]))

def run(report,acquirer=acquire,requester=request_analysis,endpoint="",model="",key=""):
    groups=components(report["results"]);cache={};results=[]
    for group in groups:
        sources=[]
        for i,s in enumerate(group):
            url=s["url"]
            if url not in cache:
                try:cache[url]={"text":acquirer(url)}
                except (OSError,ValueError,PermissionError,TimeoutError,urllib.error.URLError) as e:
                    cache[url]={"error":type(e).__name__}
            record={"id":f"S{i+1}","title":s["title"],"url":url,"publisher":s.get("publisher")}
            if "text" in cache[url]:record["passages"]=passages(cache[url]["text"][:8500],f"S{i+1}P",max_passages=18)
            else:record["acquisition_error"]=cache[url]["error"]
            sources.append(record)
        base={"sources":[{"id":s["id"],"title":s["title"],"url":s["url"],"publisher":s["publisher"]} for s in sources],
              "status":"insufficient_text","decision":None}
        if any(not s.get("passages") for s in sources):
            results.append(base);continue
        try:
            proposal,usage=requester([{"role":"system","content":SYSTEM},
                 {"role":"user","content":json.dumps({"sources":sources},ensure_ascii=False)}],endpoint,model,key)
            ids={s["id"] for s in sources}
            inc=proposal.get("included_ids",[]);exc=proposal.get("excluded_ids",[])
            if not isinstance(inc,list) or not isinstance(exc,list):inc=[];exc=[]
            ev=proposal.get("evidence_ids",{})
            if not isinstance(ev,dict):ev={}
            valid=bool(set(inc).issubset(ids) and set(exc).issubset(ids) and
                not (set(inc)&set(exc)) and set(inc)|set(exc)==ids and
                all(ev.get(s["id"]) in {p["id"] for p in s["passages"]} for s in sources if s["id"] in inc))
            decision=proposal.get("decision")
            tags=proposal.get("tags",[])
            results.append({**base,"status":"reviewed","decision":decision if decision in ("card_candidate","split_or_uncertain") else "invalid",
                "included_ids":inc,"excluded_ids":exc,"evidence_ids_valid":valid,
                "card_candidate_for_review":bool(valid and decision=="card_candidate" and len(inc)>=2),
                "card_title":str(proposal.get("card_title",""))[:200],
                "reason":str(proposal.get("reason",""))[:750],
                "tags":[str(x)[:70] for x in tags[:7]] if isinstance(tags,list) else [],
                "topic_suggestion":proposal.get("topic_suggestion"),"usage":usage})
        except (OSError,ValueError,TypeError,KeyError,TimeoutError,urllib.error.URLError) as e:
            results.append({**base,"status":"error","error_type":type(e).__name__,
                            "http_status":getattr(e,"code",None),"provider_error_code":provider_error_code(e)})
    return {"schema_version":1,"method":"frozen_llm_edges_plus_whole_group_qwen_review",
       "summary":{"initial_same_news_pairs":sum(r.get("relation")=="same_news_development" for r in report["results"]),
          "candidate_components":len(groups),"candidate_groups_of_three_or_more":sum(len(g)>=3 for g in groups),
          "reviewed_groups":sum(r["status"]=="reviewed" for r in results),
          "card_candidates_for_review":sum(r.get("card_candidate_for_review",False) for r in results),
          "unique_source_urls":len(cache),"substantial_source_urls":sum("text" in x for x in cache.values())},
       "groups":results,
       "limitations":["Uses exact frozen 54-pair pilot; only its same-news edges seed card candidates.",
          "A connected component is a proposal, not an automatic transitive merge.",
          "Every component is rechecked jointly against original substantial texts.",
          "Other relation labels remain cross-card/topic/issue links, not merged cards.",
          "No original texts persisted, no public cards/topics/nuclei created.",
          "LLM verdicts and tag suggestions require editorial validation."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not (endpoint and model and key):p.error("Missing LLM credentials")
    result=run(json.loads(a.input.read_text()),endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Multi-source Qwen card review:",json.dumps(result["summary"]))
    for i,g in enumerate(result["groups"],1):
        print("GROUP",i,json.dumps({"status":g["status"],"decision":g.get("decision"),
              "included_ids":g.get("included_ids"),"excluded_ids":g.get("excluded_ids"),
              "card_title":g.get("card_title"),"tags":g.get("tags"),
              "reason":g.get("reason")},ensure_ascii=False))
if __name__=="__main__":main()
