"""Produce an auditable stratified editorial review queue from pilot outputs."""
import argparse,json,random
from pathlib import Path
def build(taxonomy,hybrid,seed=20261014):
 rng=random.Random(seed)
 docs=taxonomy.get("documents",[])
 buckets={"fine_proposed":[],"fine_abstained":[],"macro_abstained":[]}
 for d in docs:
  if d.get("proposed_category"):buckets["fine_proposed"].append(d)
  else:buckets["fine_abstained"].append(d)
  if not d.get("macro_category_candidate"):buckets["macro_abstained"].append(d)
 sample=[]
 for name,items in buckets.items():
  chosen=rng.sample(items,min(20,len(items)))
  sample.extend({"stratum":name,"url":d["url"],"title":d["title"],
   "macro_candidate":d.get("macro_category_candidate"),"fine_candidate":d.get("proposed_category"),
   "review_macro_gold":None,"review_fine_gold":None} for d in chosen)
 pairs=hybrid.get("pairs",[])
 positive=[p for p in pairs if p["decision"]=="same_event_review_candidate"]
 other=[p for p in pairs if p["decision"]!="same_event_review_candidate"]
 review=[]
 for name,items in (("candidate_same_event",positive),("unresolved",other)):
  review.extend({"stratum":name,"url_a":p["url_a"],"title_a":p["title_a"],
   "url_b":p["url_b"],"title_b":p["title_b"],"hybrid_score":p["hybrid_score"],
   "semantic_similarity":p["semantic_similarity"],"gold_relation":None} for p in rng.sample(items,min(25,len(items))))
 return {"schema_version":1,"seed":seed,"category_review":sample,"pair_review":review,
 "allowed_pair_labels":["same_event","related_event","same_topic_only","unrelated"],
 "notes":["Gold labels must be entered independently; unreviewed samples are not accuracy measurements.",
 "Sampling is stratified, not prevalence-weighted; do not report raw sample accuracy as corpus accuracy."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--taxonomy",type=Path,required=True);p.add_argument("--hybrid",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 result=build(json.loads(a.taxonomy.read_text()),json.loads(a.hybrid.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"category_review":len(result["category_review"]),"pair_review":len(result["pair_review"])}))
if __name__=="__main__":main()
