"""One bounded critical split review per consolidated case, metadata only.

Reject invented corroboration, unrelated developments and transitive mergers.
Every group is provisional, never automatically published.
"""
import argparse,json,os,urllib.error
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("You are Ubik's adversarial editor. The input is a review CASE, NOT a card. "
"Prior overlapping proposals may contradict each other. Review all original "
"titles, RSS descriptions, publishers, dates, and all proposal variants. "
"Partition into DISJOINT groups of >=2 sources only where almost all central "
"facts concern the same specific development. Separate later reactions, "
"photos, interviews, related attacks, and different incidents. Leave "
"ambiguous sources standalone. Do not infer facts absent from metadata. "
"Return JSON {cards:[{source_ids:[...],central_development:string,"
"reason:string}],standalone_source_ids:[...],related_distinct:"
"[{source_ids:[...],reason:string}],uncertainties:[string]}. "
"Only provided source IDs; never duplicate an ID across cards. "
"Every card remains provisional and requires text evidence before verified synthesis.")

def run(data,requester=request_analysis,endpoint="",model="",key="",limit=8):
    reviews=[]
    for case in data["cases"][:limit]:
        payload={"case_id":case["case_id"],"sources":case["sources"],
                 "prior_proposals":case["proposal_variants"]}
        try:
            answer,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
                endpoint,model,key,timeout=35)
            allowed=set(case["source_ids"]);used=set();cards=[];rejected=[]
            raw=answer.get("cards",[])
            if not isinstance(raw,list):raw=[]
            for card in raw:
                ids=card.get("source_ids",[]) if isinstance(card,dict) else []
                if not isinstance(ids,list) or len(ids)<2 or len(set(ids))!=len(ids) or not set(ids)<=allowed or used.intersection(ids):
                    rejected.append(ids);continue
                used.update(ids)
                cards.append({"source_ids":ids,"central_development":card.get("central_development",""),
                    "reason":card.get("reason",""),"status":"metadata_only_provisional"})
            reviews.append({"case_id":case["case_id"],"status":"reviewed",
                "cards":cards,"standalone_source_ids":sorted(allowed-used),
                "invalid_proposals":rejected,"uncertainties":answer.get("uncertainties",[]),
                "related_distinct":answer.get("related_distinct",[]),"usage":usage})
        except (ValueError,KeyError,TypeError,TimeoutError,urllib.error.URLError) as e:
            reviews.append({"case_id":case["case_id"],"status":"error","error_type":type(e).__name__})
    return {"summary":{"review_cases":len(data["cases"]),"attempted":len(reviews),
        "completed":sum(r["status"]=="reviewed" for r in reviews),
        "errors":sum(r["status"]=="error" for r in reviews),
        "provisional_cards":sum(len(r.get("cards",[])) for r in reviews)},
        "reviews":reviews,"limitations":["Only metadata and prior model proposals examined.",
          "No full-text verification or independent fact checking.",
          "Unreviewed cases remain unresolved; no automatic publication."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--limit",type=int,default=8)
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not all((endpoint,model,key)):p.error("Missing LLM configuration")
    result=run(json.loads(a.input.read_text()),endpoint=endpoint,model=model,key=key,limit=a.limit)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("CRITICAL_REVIEW",json.dumps(result["summary"]))
    for review in result["reviews"]:
        print("CASE",review["case_id"],review["status"],"cards",json.dumps(review.get("cards",[]),ensure_ascii=False))
if __name__=="__main__":main()
