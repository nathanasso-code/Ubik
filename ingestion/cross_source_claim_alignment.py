"""Build a privacy-conscious, bounded claim-alignment diagnostic from transient article text.

This is NOT an LLM; it produces inspectable aggregate signals and abstains from
declaring contradictions. Original extracted bodies are never persisted.
"""
import argparse,collections,json,re
from pathlib import Path
from ingestion.cross_source_claim_probe import fetch_claims

STOP=set("the and that this with from into when where were have been their which while about after before says said also there over under more than then would could should some many most very first last news report reported according people year years days months time".split())
def terms(s):
    return set(t for t in re.findall(r"[a-z]{3,}",s.lower()) if t not in STOP)
def compare(a,b):
    left=a.get("claims",[]);right=b.get("claims",[])
    scored=[]
    for i,x in enumerate(left):
        ta=terms(x["excerpt"])
        for j,y in enumerate(right):
            tb=terms(y["excerpt"])
            shared=ta&tb
            score=len(shared)/len(ta|tb) if ta|tb else 0
            if score<0.16 or len(shared)<2:continue
            na=set(x["numbers"]);nb=set(y["numbers"])
            scored.append({"left_index":i,"right_index":j,"lexical_overlap":round(score,3),
                           "shared_terms":len(shared),"numeric_overlap":len(na&nb),
                           "numeric_mismatch_candidate":bool(na and nb and na!=nb)})
    scored.sort(key=lambda r:-r["lexical_overlap"])
    return scored[:12]
def analyze(data,checker=fetch_claims):
    pairs=[p for p in data["pairs"] if p.get("both_800_100")]
    urls=sorted({s["url"] for p in pairs for s in (p["left"],p["right"])})
    evidence={u:checker(u) for u in urls}
    records=[]
    for p in pairs:
        a,b=p["left"],p["right"]
        x,y=evidence[a["url"]],evidence[b["url"]]
        matches=compare(x,y) if x["status"]=="text_available" and y["status"]=="text_available" else []
        records.append({"left_url":a["url"],"right_url":b["url"],
                        "both_text_available":x["status"]=="text_available" and y["status"]=="text_available",
                        "left_claim_count":len(x.get("claims",[])),"right_claim_count":len(y.get("claims",[])),
                        "candidate_claim_alignments":matches,
                        "relation":"unverified"})
    return {"schema_version":1,"method":"transient_numbered_sentence_token_overlap",
            "summary":{"candidate_pairs":len(records),
                       "pairs_both_available":sum(p["both_text_available"] for p in records),
                       "pairs_with_candidate_alignment":sum(bool(p["candidate_claim_alignments"]) for p in records),
                       "candidate_alignments":sum(len(p["candidate_claim_alignments"]) for p in records),
                       "numeric_mismatch_candidates":sum(x["numeric_mismatch_candidate"] for p in records for x in p["candidate_claim_alignments"])},
            "pairs":records,
            "limitations":["No semantic entailment, event identity, or contradiction verdict is inferred.",
                           "Number mismatch may be unrelated quantities, dates or updates.",
                           "Only sentences with digits are examined; missing claims do not imply absence.",
                           "Extracted text and sentence excerpts are not persisted."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();r=analyze(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("Cross-source claim alignment:",json.dumps(r["summary"]))
if __name__=="__main__":main()
