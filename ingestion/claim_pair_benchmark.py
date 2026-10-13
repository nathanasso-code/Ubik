"""Small synthetic regression set for candidate claim relations."""
import argparse,json
from pathlib import Path
from ingestion.cross_source_evidence_review import relate
CASES=[
("The trial showed reduced symptoms in adult patients.","The trial showed reduced symptoms in adult patients.","possible_redundancy_review"),
("The trial showed reduced symptoms in adult patients.","The trial showed no reduced symptoms in adult patients.","possible_polarity_difference_review"),
("The trial showed reduced symptoms in adult patients.","Ocean temperatures rose during summer.","insufficient_overlap"),
]
def evaluate():
 rows=[{"expected":label,"predicted":relate(a,b)["relation"]} for a,b,label in CASES]
 return {"schema_version":1,"dataset":"synthetic_regression_examples",
 "coverage":{"pairs":len(rows),"matched":sum(r["expected"]==r["predicted"] for r in rows)},
 "cases":rows,"limitations":["Synthetic regression only, not real-world accuracy."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
 a=p.parse_args();result=evaluate()
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n")
 print(result["coverage"])
if __name__=="__main__":main()
