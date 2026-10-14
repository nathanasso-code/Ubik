"""Turn blinded statement packets into independent adjudication-ready CSV files.

Import requires two independent reviewer labels and agreement; disputed items
remain unresolved. No model predictions enter the reviewer files.
"""
import argparse,csv,json
from pathlib import Path

EVENT={"same_event","related_different_event","different_event","uncertain"}
REL={"equivalent","a_entails_b","b_entails_a","contradiction","unrelated","uncertain"}
FIELDS=["item_id","url_a","url_b","statement_index","statement_a","statement_b",
        "event_identity","statement_relation","evidence_sufficient","source_notes"]
def export(packet,output):
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open("w",newline="",encoding="utf-8") as f:
  writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader()
  for item in packet["items"]:
   writer.writerow({k:item.get(k,"") for k in FIELDS})
 return len(packet["items"])
def read_csv(path):
 with path.open(newline="",encoding="utf-8") as f:
  rows=list(csv.DictReader(f))
 out={}
 for row in rows:
  k=row["item_id"]
  if not k or k in out:raise ValueError("Missing or duplicate item_id")
  if row["event_identity"] not in EVENT or row["statement_relation"] not in REL:
   raise ValueError("Incomplete or invalid annotation for "+k)
  if row["evidence_sufficient"] not in ("yes","no","unknown"):
   raise ValueError("Invalid evidence_sufficient for "+k)
  out[k]=row
 return out
def adjudicate(packet,reviewer_a,reviewer_b):
 a,b=read_csv(reviewer_a),read_csv(reviewer_b)
 expected={x["item_id"] for x in packet["items"]}
 if set(a)!=expected or set(b)!=expected:raise ValueError("Reviewer IDs do not match packet")
 agreement=[];disputed=[]
 for item in packet["items"]:
  k=item["item_id"];x,y=a[k],b[k]
  fields=("event_identity","statement_relation","evidence_sufficient")
  if all(x[z]==y[z] for z in fields):
   agreement.append({"item_id":k,"url_a":item["url_a"],"url_b":item["url_b"],
    "statement_index":item["statement_index"],"event_identity":x["event_identity"],
    "statement_relation":x["statement_relation"],"evidence_sufficient":x["evidence_sufficient"],
    "review_status":"independent_agreement"})
  else:
   disputed.append({"item_id":k,"review_status":"requires_adjudication",
                    "reviewer_a":{z:x[z] for z in fields},"reviewer_b":{z:y[z] for z in fields}})
 return {"schema_version":1,"agreed":agreement,"disputed":disputed,
  "coverage":{"total":len(expected),"agreed":len(agreement),"disputed":len(disputed)},
  "limitations":["Reviewer agreement does not guarantee factual correctness.",
   "Disputed annotations cannot be silently converted into gold labels."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--packet",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True)
 p.add_argument("--reviewer-a",type=Path);p.add_argument("--reviewer-b",type=Path)
 args=p.parse_args();packet=json.loads(args.packet.read_text())
 if bool(args.reviewer_a)!=bool(args.reviewer_b):p.error("Both reviewers are required")
 if args.reviewer_a:
  result=adjudicate(packet,args.reviewer_a,args.reviewer_b)
  args.output.parent.mkdir(parents=True,exist_ok=True)
  args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
  print(json.dumps(result["coverage"]))
 else:print(json.dumps({"exported":export(packet,args.output)}))
if __name__=="__main__":main()
