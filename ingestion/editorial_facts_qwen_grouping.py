"""Ask Qwen to group independently reviewed facts only, without seeing original text."""
import json,os,argparse
from pathlib import Path
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM="""You are a strict event-identity adjudicator. The source summaries were independently reviewed against original article text. You must NOT re-extract or invent facts. Group only source IDs describing the SAME specific central development. Do not merge a decision with reactions to it, interviews, later developments, opinion/editorial responses, or thematic neighbors. The same statement reported by multiple outlets may merge. Podcast and video versions of the same episode may merge if clearly the same editorial work, but note they are not independent confirmations. Sources marked insufficient stay standalone. For each proposed card cite the exact common actor+action+object in reason. When uncertain leave standalone. Return JSON object cards:[{source_ids:[...],reason:string}], related_events:[{source_ids:[...],relation:string}], uncertainties:[string]."""
def run(baseline,editorial,requester=request_analysis):
    facts={f["source_id"]:f for f in editorial["facts"]}
    reviews=[];errors=[];calls=0
    for case in baseline["reviews"]:
        ids=case["source_ids"]
        payload={"sources":[facts[i] for i in ids]}
        calls+=1
        try:
            answer,usage=requester([{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload)}],
                os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=90)
            cards=[];used=set();invalid=[]
            for card in answer.get("cards",[]):
                members=card.get("source_ids",[])
                if not isinstance(members,list) or len(members)<2 or len(set(members))!=len(members) or not set(members)<=set(ids) or used.intersection(members) or any(facts[i]["information_quality"]!="substantive" for i in members):
                    invalid.append(card);continue
                used.update(members);cards.append({"source_ids":sorted(members),"reason":card.get("reason","")})
            reviews.append({"source_ids":ids,"cards":cards,"standalone_source_ids":sorted(set(ids)-used),"invalid_groups":invalid,"related_events":answer.get("related_events",[]),"uncertainties":answer.get("uncertainties",[]),"usage":usage})
        except Exception as e:
            errors.append({"source_ids":ids,"error":str(e)[:200]})
    return {"summary":{"contexts":len(reviews),"calls":calls,"errors":len(errors),"cards":sum(len(r["cards"]) for r in reviews)},"reviews":reviews,"errors":errors}
def main():
    p=argparse.ArgumentParser();p.add_argument("baseline",type=Path);p.add_argument("editorial",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    result=run(json.loads(a.baseline.read_text()),json.loads(a.editorial.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("EDITORIAL_FACTS_QWEN_GROUPING",json.dumps(result["summary"]))
if __name__=="__main__":main()
