"""Controlled test: central-focus extraction, with and without explicit no-group prior."""
import argparse,json,os
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis
from ingestion.frozen_qwen_summary_focus import SYSTEM as BASE
NEUTRAL = BASE
ABSTAIN = BASE + """
CRITICAL EXPERIMENTAL PRIOR: These sources were selected by lexical/semantic similarity, NOT because they report the same event. Many candidate sets have ZERO valid pairs. A completely empty cards array is a normal, successful outcome. Do not seek a grouping to satisfy the task. Judge each source independently and prefer standalone when evidence of exact central-development identity is absent. Relatedness is not identity. For each proposed card, explicitly test whether removing shared background leaves the SAME primary news event for every member. If not, reject the card. Do not invent a broad shared_development to justify a group."""
def run(graph,metadata,texts,requester=request_analysis,endpoint="",model="",key="",max_calls=20):
    byid={s["id"]:s for s in graph["sources"]}
    extracted={s["source_id"]:s for s in texts["sources"] if s.get("status")=="extracted_unverified" and len(s.get("text",""))>=800}
    out={}
    for variant,system in (("baseline",NEUTRAL),("abstention",ABSTAIN)):
        reviews=[];errors=[];skipped=[];calls=0
        for case in metadata["reviews"]:
            ids=[sid for sid in case["source_ids"] if sid in extracted]
            if len(ids)<2:
                skipped.append({"source_ids":case["source_ids"],"reason":"fewer_than_two_substantial_texts"});continue
            if calls>=max_calls:break
            calls+=1
            payload={"sources":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"],"article_body":extracted[sid]["text"][:7000]} for sid in ids]}
            try:
                answer,usage=requester([{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],endpoint,model,key,timeout=90)
                sources=answer.get("sources",[])
                if not isinstance(sources,list) or len(sources)!=len(ids) or set(s.get("source_id") for s in sources)!=set(ids):raise ValueError("source_ids_mismatch")
                eligible={s["source_id"] for s in sources if s.get("quality")=="substantive" and isinstance(s.get("central_focus"),str) and s["central_focus"].strip() and isinstance(s.get("summary"),str) and s["summary"].strip()}
                cards=[];invalid=[];used=set()
                for c in answer.get("cards",[]):
                    members=c.get("source_ids",[])
                    if not isinstance(members,list) or len(members)<2 or len(members)!=len(set(members)) or not set(members)<=eligible or used.intersection(members):
                        invalid.append(c);continue
                    used.update(members);cards.append(c)
                reviews.append({"source_ids":ids,"sources":sources,"cards":cards,"standalone_source_ids":sorted(set(ids)-used),"invalid_groups":invalid,"related_events":answer.get("related_events",[]),"uncertainties":answer.get("uncertainties",[]),"usage":usage})
            except Exception as exc:errors.append({"source_ids":ids,"error":str(exc)[:300]})
        out[variant]={"summary":{"contexts":len(reviews),"calls":calls,"sources":sum(len(r["sources"]) for r in reviews),"cards":sum(len(r["cards"]) for r in reviews),"errors":len(errors)},"reviews":reviews,"errors":errors,"skipped":skipped}
    return out
def main():
    p=argparse.ArgumentParser()
    for n in ("graph","metadata","texts"):p.add_argument(n,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    data=[json.loads(getattr(a,n).read_text()) for n in ("graph","metadata","texts")]
    result=run(*data,endpoint=os.environ["UBIK_LLM_ENDPOINT"],model=os.environ["UBIK_LLM_MODEL"],key=os.environ["UBIK_LLM_API_KEY"])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("ABSTENTION_TEST",json.dumps({k:v["summary"] for k,v in result.items()}))
if __name__=="__main__":main()
