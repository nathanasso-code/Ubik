"""Create blinded human annotation packets from real statement comparisons.

The annotator sees original text and URLs, not NLI labels/scores or
model-generated risk flags. This prevents easy confirmation bias.
"""
import argparse,json,hashlib
from pathlib import Path

LABELS=["equivalent","a_entails_b","b_entails_a","contradiction","unrelated","uncertain"]
def packet(audit):
 records=[]
 for row in audit.get("review_queue",[]):
  key=f'{row["url_a"]}|{row["url_b"]}|{row["statement_index"]}'
  records.append({"item_id":hashlib.sha256(key.encode()).hexdigest()[:16],
   "url_a":row["url_a"],"url_b":row["url_b"],"statement_index":row["statement_index"],
   "statement_a":row["text_a"],"statement_b":row["text_b"],
   "event_identity_gold":None,"statement_relation_gold":None,
   "evidence_sufficient_gold":None,"annotator_notes":"",
   "review_status":"unannotated"})
 # Stable, content-derived ordering; no model score or prediction influences order.
 records.sort(key=lambda x:x["item_id"])
 return {"schema_version":1,"instructions":{
  "event_identity_gold":"same_event | related_different_event | different_event | uncertain",
  "statement_relation_gold":LABELS,
  "evidence_sufficient_gold":"true | false | null; null means not assessed",
  "protocol":"Read both original sources independently where legally accessible. Judge event identity separately from statement entailment. Mark uncertain when context is insufficient. Never infer gold from model predictions."},
  "items":records,"coverage":{"items":len(records),"annotated":0},
  "limitations":["Unannotated packet is not a gold benchmark.","URLs may become unavailable."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--audit",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
 a=p.parse_args();result=packet(json.loads(a.audit.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
