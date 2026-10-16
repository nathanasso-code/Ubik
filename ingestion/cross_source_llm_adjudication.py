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

SYSTEM=("Compare two source articles. Output JSON with relation one of "
        "same_event, related_distinct_event, different_event, uncertain; "
        "reason a short explanation, quote_a and quote_b each an exact short "
        "verbatim substring from the corresponding article text (maximum 100 characters), "
        "and distinct_details as a list of up to three concise differences. "
        "Never infer that differing numbers contradict without aligning their meaning and date. "
        "If insufficient evidence choose uncertain.")
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
    qa,qb=proposal.get("quote_a"),proposal.get("quote_b")
    valid_quotes=all(isinstance(q,str) and 12<=len(q)<=100 and q in body
                     for q,body in ((qa,a),(qb,b)))
    details=proposal.get("distinct_details",[])
    if not isinstance(details,list):details=[]
    return {"relation":relation if valid_relation else "invalid",
            "grounded_quotes":valid_quotes,
            "quote_a_valid":isinstance(qa,str) and 12<=len(qa)<=100 and qa in a,
            "quote_b_valid":isinstance(qb,str) and 12<=len(qb)<=100 and qb in b,
            "quote_a_length":len(qa) if isinstance(qa,str) else None,
            "quote_b_length":len(qb) if isinstance(qb,str) else None,
            "accepted_for_review":valid_relation and valid_quotes,
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
def run(data,limit=4,execute=False,endpoint="",model="",key="",acquirer=acquire,requester=request_analysis):
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
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps({
                "a":{"title":a["title"],"text":ta[:7000]},
                "b":{"title":b["title"],"text":tb[:7000]}},ensure_ascii=False)}]
            proposal,usage=requester(messages,endpoint,model,key)
            result=evaluate(proposal,ta[:7000],tb[:7000])
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
               "Substring-grounded quotations are a weak but necessary condition, not semantic proof.",
               "No original texts or verbatim quotations are persisted."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int,default=4);p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","")
    model=os.getenv("UBIK_LLM_MODEL","")
    key=os.getenv("UBIK_LLM_API_KEY","")
    if a.execute and not (endpoint and model and key):p.error("Missing LLM endpoint/model/key")
    result=run(json.loads(a.input.read_text()),limit=min(4,max(1,a.limit)),
               execute=a.execute,endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("LLM cross-source adjudication:",json.dumps(result["summary"]))
if __name__=="__main__":main()
