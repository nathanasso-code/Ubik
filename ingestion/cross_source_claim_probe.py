"""Transient claim-evidence comparison of already-accessible cross-source pairs.

Article bodies are kept in memory only. Evidence output contains short
excerpts (<=160 chars) with source URL and claim number, not article bodies.
No automatic factual contradiction verdict is asserted.
"""
import argparse,collections,json,re
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import fetch_one,USER_AGENT

def sentences(text):
    chunks=re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])",text)
    return [x.strip() for x in chunks if len(x.strip())>=45 and len(x.split())>=8]
def extract_claims(text,max_claims=16):
    out=[];seen=set()
    for s in sentences(text):
        numbers=re.findall(r"(?<!\w)\d+(?:[.,]\d+)?(?:%|\b)",s)
        if not numbers:continue
        key=s[:90].lower()
        if key in seen:continue
        seen.add(key)
        out.append({"excerpt":s[:160],"numbers":numbers[:8]})
        if len(out)>=max_claims:break
    return out
def fetch_claims(url,fetch=fetch_one):
    host=urlsplit(url).hostname
    try:
        robots=fetch("https://"+host+"/robots.txt",{host},timeout=5)
        parser=RobotFileParser();parser.parse(robots.splitlines())
        if not parser.can_fetch(USER_AGENT,url):return {"status":"robots_disallowed","claims":[]}
        raw=fetch(url,{host},timeout=7)
        import trafilatura
        text=trafilatura.extract(raw,include_comments=False,include_tables=False) or ""
        if len(text)<800 or len(text.split())<100:
            return {"status":"insufficient_text","chars":len(text),"claims":[]}
        return {"status":"text_available","chars":len(text),"claims":extract_claims(text)}
    except (OSError,TimeoutError,ValueError,PermissionError) as exc:
        return {"status":"fetch_failed","error_type":type(exc).__name__,"claims":[]}
def analyze(data,checker=fetch_claims):
    pairs=[p for p in data["pairs"] if p.get("both_800_100")]
    urls=sorted({s["url"] for p in pairs for s in (p["left"],p["right"])})
    checked={url:checker(url) for url in urls}
    records=[]
    for p in pairs:
        a,b=p["left"],p["right"]
        left,right=checked[a["url"]],checked[b["url"]]
        nums_a={n for claim in left.get("claims",[]) for n in claim["numbers"]}
        nums_b={n for claim in right.get("claims",[]) for n in claim["numbers"]}
        records.append({"left":{"url":a["url"],"title":a["title"],"status":left["status"],"claims":left.get("claims",[])},
                        "right":{"url":b["url"],"title":b["title"],"status":right["status"],"claims":right.get("claims",[])},
                        "both_text_available":left["status"]=="text_available" and right["status"]=="text_available",
                        "shared_numeric_tokens":sorted(nums_a&nums_b),
                        "different_numeric_tokens_left":sorted(nums_a-nums_b),
                        "different_numeric_tokens_right":sorted(nums_b-nums_a),
                        "relation":"unverified"})
    return {"schema_version":1,"summary":{"candidate_pairs":len(pairs),"unique_urls":len(urls),
             "text_available":sum(x["status"]=="text_available" for x in checked.values()),
             "pairs_both_available":sum(x["both_text_available"] for x in records),
             "numbered_claims":sum(len(x.get("claims",[])) for x in checked.values())},
            "pairs":records,"limitations":["Numbers from different sentences cannot be treated as contradictory without claim alignment.",
            "160-character evidence snippets may still be copyright-protected; do not redistribute without rights review.",
            "No full text persisted, no LLM, no verified same-event or contradiction labels."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();r=analyze(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    # Excerpts are intentionally not uploaded: persist only counts and URL-level signals.
    sanitized={"schema_version":r["schema_version"],"summary":r["summary"],
      "pairs":[{"left":{"url":p["left"]["url"],"status":p["left"]["status"],"claim_count":len(p["left"]["claims"])},
                "right":{"url":p["right"]["url"],"status":p["right"]["status"],"claim_count":len(p["right"]["claims"])},
                "both_text_available":p["both_text_available"],
                "shared_numeric_token_count":len(p["shared_numeric_tokens"]),
                "left_only_numeric_token_count":len(p["different_numeric_tokens_left"]),
                "right_only_numeric_token_count":len(p["different_numeric_tokens_right"]),
                "relation":"unverified"} for p in r["pairs"]],
      "limitations":r["limitations"]}
    a.output.write_text(json.dumps(sanitized,ensure_ascii=False,indent=2)+"\n")
    print("Transient claim extraction:",json.dumps(r["summary"]))
if __name__=="__main__":main()
