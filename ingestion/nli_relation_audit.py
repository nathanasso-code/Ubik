"""Auditable diagnostics for real NLI predictions; no invented gold labels."""
import argparse,json
from collections import Counter
from pathlib import Path

def audit(payload):
 rows=[]
 for edge in payload.get("edges",[]):
  for idx,c in enumerate(edge.get("comparisons",[])):
   nli=c.get("directional_nli",{})
   a,b=nli.get("a_to_b",{}),nli.get("b_to_a",{})
   if not a or not b:continue
   la,lb=a.get("label"),b.get("label")
   flags=[]
   if "contradiction" in (la,lb) and la!=lb:
    flags.append("asymmetric_contradiction")
   if la==lb=="neutral" and c.get("lexical_overlap",0)>=0.4:
    flags.append("high_overlap_both_neutral")
   if la==lb=="contradiction":
    flags.append("symmetric_contradiction_review")
   if la==lb=="entailment":
    flags.append("bidirectional_entailment_review")
   rows.append({"url_a":edge["url_a"],"url_b":edge["url_b"],"statement_index":idx,
    "text_a":c["statement_a"]["text"],"text_b":c["statement_b"]["text"],
    "lexical_overlap":c.get("lexical_overlap"),"labels":[la,lb],
    "scores":[a.get("score"),b.get("score")],"flags":flags,
    "human_label":None,"human_review_status":"pending"})
 counts=Counter(flag for row in rows for flag in row["flags"])
 return {"schema_version":1,"review_queue":sorted(rows,key=lambda r:(-bool(r["flags"]),-len(r["flags"]),r["url_a"])),
  "coverage":{"statement_pairs":len(rows),"flag_counts":dict(counts),"flagged_pairs":sum(bool(r["flags"]) for r in rows),
   "gold_labeled_pairs":0,"precision":None,"recall":None},
  "limitations":["Diagnostic flags are not evidence of actual model errors.",
   "Gold labels require independent human adjudication of source text.",
   "No accuracy or precision can be computed from unlabeled examples."]}

def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
 a=p.parse_args();result=audit(json.loads(a.input.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
