"""Controlled single-source acquisition to claim candidates; no automatic publication."""
import argparse,json
from pathlib import Path
from ingestion.approved_https_fetch import fetch_authorized
from ingestion.authorized_source_text import capture_authorized_html
from ingestion.source_claim_candidates import claim_candidates

def run(url,policy,*,fetch=fetch_authorized):
    fetched=fetch(url,policy)
    captured=capture_authorized_html(url,fetched["html"],access_authorized=True)
    captured["retrieved_at_utc"]=fetched.get("retrieved_at_utc")
    captured["robots_checked"]=fetched.get("robots_checked",False)
    captured["rights_confirmed_by_operator"]=fetched.get("rights_confirmed_by_operator",False)
    sources={url:captured}
    return {"sources":sources,"claims":claim_candidates(sources),
            "published":False,"verified_claims":0}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url",required=True);p.add_argument("--policy",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=run(a.url,json.loads(a.policy.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"source_count":len(result["sources"]),"verified_claims":0,"published":False}))
if __name__=="__main__":main()
