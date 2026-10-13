"""Evaluate manually labeled review samples; refuse to invent gold labels."""
import argparse,json
from collections import Counter
from pathlib import Path
VALID={"same_event","related_event","same_topic_only","unrelated"}
def evaluate(review):
 pairs=review.get("pair_review",[])
 labeled=[p for p in pairs if p.get("gold_relation") in VALID]
 predicted=[p for p in labeled if p["stratum"]=="candidate_same_event"]
 tp=sum(p["gold_relation"]=="same_event" for p in predicted)
 fp=len(predicted)-tp
 fn=sum(p["gold_relation"]=="same_event" for p in labeled if p["stratum"]!="candidate_same_event")
 precision=tp/(tp+fp) if tp+fp else None
 recall=tp/(tp+fn) if tp+fn else None
 categories=review.get("category_review",[])
 macro=[d for d in categories if d.get("review_macro_gold") is not None and d.get("macro_candidate") is not None]
 fine=[d for d in categories if d.get("review_fine_gold") is not None and d.get("fine_candidate") is not None]
 return {"schema_version":1,"annotation_coverage":{"pair_labeled":len(labeled),"pair_total":len(pairs),
 "macro_labeled_proposals":len(macro),"fine_labeled_proposals":len(fine)},
 "pair_candidate_precision_on_labeled":precision,"pair_candidate_recall_on_labeled":recall,
 "macro_accuracy_on_labeled_proposals":sum(d["review_macro_gold"]==d["macro_candidate"] for d in macro)/len(macro) if macro else None,
 "fine_accuracy_on_labeled_proposals":sum(d["review_fine_gold"]==d["fine_candidate"] for d in fine)/len(fine) if fine else None,
 "warning":"Stratified review is not representative of corpus prevalence; recall excludes unproposed pairs outside sample."}
def main():
 p=argparse.ArgumentParser();p.add_argument("--review",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 result=evaluate(json.loads(a.review.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result["annotation_coverage"]))
if __name__=="__main__":main()
