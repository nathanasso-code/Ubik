"""Evaluate NLI review predictions only against independently supplied gold labels.

Gold JSON: {"annotations":[{"url_a":"...","url_b":"...","statement_index":0,
"label":"equivalent|a_entails_b|b_entails_a|contradiction|unrelated|uncertain"}]}.
No labels are inferred from model outputs.
"""
import argparse,json
from collections import Counter
from pathlib import Path

VALID={"equivalent","a_entails_b","b_entails_a","contradiction","unrelated","uncertain"}
def key(x):return (x["url_a"],x["url_b"],x["statement_index"])
def prediction(row):
 a,b=row["labels"]
 if a==b=="entailment":return "equivalent"
 if a=="entailment" and b!="entailment":return "a_entails_b"
 if b=="entailment" and a!="entailment":return "b_entails_a"
 if a==b=="contradiction":return "contradiction"
 if a==b=="neutral":return "unrelated"
 return "uncertain"
def evaluate(audit,gold):
 annotations=gold.get("annotations",[])
 seen=set();lookup={}
 for a in annotations:
  k=key(a)
  if k in seen:raise ValueError("Duplicate gold annotation")
  seen.add(k)
  if a.get("label") not in VALID:raise ValueError("Unknown gold label")
  lookup[k]=a["label"]
 pairs=[]
 for row in audit.get("review_queue",[]):
  k=key(row)
  if k not in lookup:continue
  expected=lookup[k];predicted=prediction(row)
  pairs.append({"url_a":k[0],"url_b":k[1],"statement_index":k[2],
                "gold":expected,"predicted":predicted,"match":expected==predicted})
 n=len(pairs)
 return {"schema_version":1,"labeled_pairs":n,"accuracy":round(sum(p["match"] for p in pairs)/n,4) if n else None,
  "confusion":[{"gold":g,"predicted":p,"count":v} for (g,p),v in sorted(Counter((x["gold"],x["predicted"]) for x in pairs).items())],
  "cases":pairs,"limitations":["Accuracy is computed only on explicitly annotated pairs.",
   "Convenience sample accuracy is not population-level accuracy.",
   "Gold labels must be adjudicated independently from model predictions."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--audit",type=Path,required=True)
 p.add_argument("--gold",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
 a=p.parse_args();d=evaluate(json.loads(a.audit.read_text()),json.loads(a.gold.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+"\n")
 print(json.dumps({"labeled_pairs":d["labeled_pairs"],"accuracy":d["accuracy"]}))
if __name__=="__main__":main()
