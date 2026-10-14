"""Conservative NLI publication gate: only advisory evidence, never automatic truth.

Asymmetric predictions and high-overlap neutral pairs are abstentions.
Symmetric contradiction is always a review candidate, not an asserted conflict.
"""
import argparse,json
from collections import Counter
from pathlib import Path

def gate(audit):
 out=[]
 for row in audit.get("review_queue",[]):
  a,b=row["labels"];flags=row.get("flags",[])
  if "asymmetric_contradiction" in flags:
   decision="abstain_directional_conflict"
  elif a==b=="contradiction":
   decision="human_review_possible_contradiction"
  elif "high_overlap_both_neutral" in flags:
   decision="human_review_possible_paraphrase"
  elif a==b=="entailment":
   decision="human_review_possible_equivalence"
  elif a=="entailment" or b=="entailment":
   decision="human_review_directional_entailment"
  else:
   decision="abstain_insufficient_evidence"
  out.append({"url_a":row["url_a"],"url_b":row["url_b"],"statement_index":row["statement_index"],
              "decision":decision,"automatic_merge_allowed":False,
              "automatic_contradiction_claim_allowed":False,"review_status":"unreviewed"})
 return {"schema_version":1,"decisions":out,
         "coverage":{"pairs":len(out),"decision_counts":dict(Counter(x["decision"] for x in out)),
                     "automatic_merges":0,"automatic_contradiction_claims":0},
         "limitations":["This gate cannot verify truth, events, or causal compatibility.",
                        "All relation proposals remain unverified and require independent evaluation."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--audit",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
 a=p.parse_args();data=gate(json.loads(a.audit.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(data["coverage"]))
if __name__=="__main__":main()
