"""Audit real discovered evidence relation proposals without claiming truth labels."""
import argparse,collections,json
from pathlib import Path
def audit(data):
 relations=data.get("relations",[])
 counts=dict(collections.Counter(r.get("relation","unknown") for r in relations))
 unique_docs=set()
 same_publisher=0
 for r in relations:
  unique_docs.update((r.get("source_a"),r.get("source_b")))
  # URLs are not reliable proxies for independent reporting.
 return {"schema_version":1,"purpose":"real_corpus_candidate_relation_audit",
 "coverage":{"candidate_pairs":len(relations),"unique_document_urls":len(unique_docs),
 "relation_types":counts,"verified_support":0,"verified_contradictions":0},
 "sample":[{"source_a":r.get("source_a"),"source_b":r.get("source_b"),
 "relation":r.get("relation"),"score":r.get("score"),
 "anchors":r.get("anchors")} for r in relations[:30]],
 "limitations":["All relations are unverified heuristic review candidates.",
 "No gold labels; no precision, recall or factual agreement can be calculated.",
 "Publisher independence, shared syndication and same-event identity not resolved."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--relations",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 result=audit(json.loads(a.relations.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
