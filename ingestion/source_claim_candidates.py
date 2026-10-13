"""Conservative claim-candidate extraction from authorized, hashed source passages.

Not an entailment model. Candidates are exact source sentences and do not
assert truth, contradiction, causation or independent corroboration.
"""
import argparse,hashlib,json,re
from pathlib import Path

_SENTENCE=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9\"“])")
def claim_candidates(sources,*,max_per_source=8):
    if not 1<=max_per_source<=30:raise ValueError("Invalid budget")
    results=[]
    for url,record in sorted(sources.items()):
        body=record.get("text")
        if not isinstance(body,str) or hashlib.sha256(body.encode("utf-8")).hexdigest()!=record.get("sha256"):
            results.append({"url":url,"status":"rejected_missing_or_changed_source","candidates":[]});continue
        seen=set();claims=[]
        for paragraph in body.splitlines():
            for sentence in _SENTENCE.split(paragraph.strip()):
                sentence=" ".join(sentence.split())
                if not 45<=len(sentence)<=600 or sentence in seen:continue
                seen.add(sentence)
                claims.append({"verbatim_quote":sentence,"source_url":url,
                               "source_sha256":record["sha256"],
                               "extraction_method":"deterministic_sentence_candidate",
                               "is_claim_verified":False,
                               "stance":"undetermined",
                               "causality":"not_assessed"})
                if len(claims)>=max_per_source:break
            if len(claims)>=max_per_source:break
        results.append({"url":url,"status":"candidate_only","candidates":claims})
    return {"schema_version":1,"purpose":"source_text_claim_candidates","sources":results,
            "automatic_verification":False,"automatic_publication":False,
            "limitations":["Sentence boundaries are heuristic and multilingual coverage is incomplete.",
                           "Quotes are candidate assertions, not parsed factual propositions.",
                           "No truth, contradiction or causal classification is performed."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("sources",type=Path);p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();result=claim_candidates(json.loads(a.sources.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"source_count":len(result["sources"]),
                      "candidate_count":sum(len(s["candidates"]) for s in result["sources"])}))
if __name__=="__main__":main()
