"""Evaluate conservative claim/evidence baseline on SciFact dev gold labels.

This baseline predicts NEI (abstain) for all claim/document pairs.
Its purpose is a reproducible honest lower bound, not semantic verification.
"""
import argparse,collections,io,json,tarfile,urllib.request
from pathlib import Path
URL="https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"
def gold_rows(blob):
 with tarfile.open(fileobj=io.BytesIO(blob),mode="r:gz") as tar:
  member=next((m for m in tar.getmembers() if m.name.endswith("/claims_dev.jsonl") or m.name=="claims_dev.jsonl"),None)
  if member is None:raise ValueError("SciFact dev labels absent")
  stream=tar.extractfile(member)
  return [json.loads(line) for line in stream if line.strip()]
def evaluate(rows):
 counts=collections.Counter();pairs=0
 for row in rows:
  for doc_id,evidences in row.get("evidence",{}).items():
   for evidence in evidences:
    counts[evidence["label"]]+=1
    pairs+=1
 return {"schema_version":1,"dataset":"SciFact development split","gold_claims":len(rows),
  "gold_evidence_rationales":pairs,"gold_label_distribution":dict(counts),
  "baseline":"always_abstain","baseline_correct_positive_predictions":0,
  "baseline_positive_recall":0.0 if pairs else None,
  "status":"measured_gold_label_coverage_not_model_accuracy",
  "limitations":["Gold rationales are not a random sample of all claim-document pairs.",
   "Always-abstain is a safety baseline, not an effective verifier.",
   "Do not report accuracy or precision for a system making zero positive predictions.",
   "Dev split is for iteration; final assessment needs a held-out labeled evaluation."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
 p.add_argument("--archive",type=Path);a=p.parse_args()
 if a.archive:blob=a.archive.read_bytes()
 else:
  with urllib.request.urlopen(URL,timeout=45) as response:
   blob=response.read(30_000_001)
  if len(blob)>30_000_000:raise ValueError("Dataset download size limit")
 result=evaluate(gold_rows(blob))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
