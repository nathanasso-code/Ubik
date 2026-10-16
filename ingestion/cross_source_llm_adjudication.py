"""Bounded Groq/OpenAI-compatible adjudication of accessible article pairs.

Full texts stay in process memory. Output stores only verdicts and grounded
quote validation flags, never copyrighted article bodies or model quotations.
"""
import argparse,json,os,re,urllib.error
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import fetch_one,USER_AGENT
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("The two news articles have already been selected as plausible candidates for describing the same real-world event. "
        "Determine whether they actually describe the SAME specific incident, regardless of lexical choices, editorial framing, protagonists emphasized, or amount of information. "
        "First compare event identity: what happened, where, when, and which actors or victims were involved. "
        "Treat omitted details and complementary facts as COMPATIBLE, not evidence of distinct events. "
        "Different wording, additional context, perspectives, or different subsets of participants do not by themselves imply different incidents. "
        "Only classify related_distinct_event or different_event when concrete identifying details establish separate incidents; "
        "distinguish a single incident from its later consequences or investigations. "
        "If evidence is insufficient, choose uncertain rather than forcing a classification. "
        "Select actual passage IDs from BOTH supplied articles as evidence, without inventing IDs, dates, or facts. "
        "Return JSON with relation (same_event, related_distinct_event, different_event, uncertain), "
        "reason (briefly explain compatible or incompatible event identifiers), "
        "evidence_a_id, evidence_b_id, and distinct_details (up to three genuine event-identity differences, not merely wording or omissions).")
def passages(text,prefix,max_passages=28):
    # Paragraphs are truncated for bounded prompts; original text stays transient.
    raw=[x.strip() for x in re.split(r"\n\s*\n",text) if len(x.strip())>=45]
    if len(raw)<2:
        raw=[x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])",text) if len(x.strip())>=45]
    return [{"id":f"{prefix}{i+1}","text":p[:360]} for i,p in enumerate(raw[:max_passages])]

def acquire(url,fetch=fetch_one):
    host=urlsplit(url).hostname
    robots=fetch("https://"+host+"/robots.txt",{host},timeout=5)
    parser=RobotFileParser();parser.parse(robots.splitlines())
    if not parser.can_fetch(USER_AGENT,url):raise PermissionError("robots disallowed")
    raw=fetch(url,{host},timeout=7)
    import trafilatura
    text=trafilatura.extract(raw,include_comments=False,include_tables=False) or ""
    if len(text)<800 or len(text.split())<100:raise ValueError("insufficient text")
    return text
def evaluate(proposal,a,b):
    relation=proposal.get("relation")
    valid_relation=relation in {"same_event","related_distinct_event","different_event","uncertain"}
    ia,ib=proposal.get("evidence_a_id"),proposal.get("evidence_b_id")
    valid_a=ia in {x["id"] for x in a} if isinstance(ia,str) else False
    valid_b=ib in {x["id"] for x in b} if isinstance(ib,str) else False
    details=proposal.get("distinct_details",[])
    if not isinstance(details,list):details=[]
    return {"relation":relation if valid_relation else "invalid",
            "evidence_a_id":ia if valid_a else None,
            "evidence_b_id":ib if valid_b else None,
            "evidence_a_valid":valid_a,"evidence_b_valid":valid_b,
            "grounded_passage_ids":valid_a and valid_b,
            "accepted_for_review":valid_relation and valid_a and valid_b,
            "reason":str(proposal.get("reason",""))[:400],
            "distinct_details":[str(x)[:160] for x in details[:3]]}

def provider_error_code(exc):
    if not isinstance(exc,urllib.error.HTTPError):return None
    try:
        body=json.loads(exc.read(8192).decode("utf-8"))
        error=body.get("error",{})
        code=error.get("code") if isinstance(error,dict) else None
        if isinstance(code,(str,int)) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}",str(code)):
            return str(code)
    except (ValueError,UnicodeError,OSError,TypeError):pass
    return None
def run(data,limit=11,execute=False,endpoint="",model="",key="",acquirer=acquire,requester=request_analysis):
    pairs=[p for p in data["pairs"] if p.get("both_800_100")][:limit]
    results=[];cache={}
    for pair in pairs:
        a,b=pair["left"],pair["right"]
        try:
            for s in (a,b):
                if s["url"] not in cache:cache[s["url"]]=acquirer(s["url"])
            ta,tb=cache[a["url"]],cache[b["url"]]
            if not execute:
                results.append({"left_url":a["url"],"right_url":b["url"],"status":"ready",
                                "chars_a":len(ta),"chars_b":len(tb)})
                continue
            pa,pb=passages(ta[:7000],"A"),passages(tb[:7000],"B")
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps({
                "a":{"title":a["title"],"passages":pa},
                "b":{"title":b["title"],"passages":pb}},ensure_ascii=False)}]
            proposal,usage=requester(messages,endpoint,model,key)
            result=evaluate(proposal,pa,pb)
            results.append({"left_url":a["url"],"right_url":b["url"],"status":"analyzed",
                            "validation":result,"usage":usage})
        except (OSError,ValueError,PermissionError,TimeoutError,KeyError,TypeError,urllib.error.URLError) as exc:
            results.append({"left_url":a["url"],"right_url":b["url"],"status":"error",
                            "error_type":type(exc).__name__,
                            "http_status":getattr(exc,"code",None),
                            "provider_error_code":provider_error_code(exc)})
    return {"schema_version":1,"model":model if execute else None,"mode":"llm" if execute else "dry_run",
            "summary":{"selected":len(results),"analyzed":sum(x["status"]=="analyzed" for x in results),
                       "grounded_for_review":sum(x.get("validation",{}).get("accepted_for_review",False) for x in results),
                       "errors":sum(x["status"]=="error" for x in results)},
            "results":results,"limitations":["LLM relations are proposals, not independently validated gold labels.",
               "Valid passage IDs prove only selection from supplied text, not semantic correctness.",
               "No original texts or verbatim passages are persisted."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int,default=11);p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","")
    model=os.getenv("UBIK_LLM_MODEL","")
    key=os.getenv("UBIK_LLM_API_KEY","")
    if a.execute and not (endpoint and model and key):p.error("Missing LLM endpoint/model/key")
    result=run(json.loads(a.input.read_text()),limit=min(11,max(1,a.limit)),
               execute=a.execute,endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("LLM cross-source adjudication:",json.dumps(result["summary"]))
if __name__=="__main__":main()
