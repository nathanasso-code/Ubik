"""Post-retrieval editorial review queue; NEVER modifies frozen semantic rankings.

Balances high-similarity duplicate candidates and lower-scoring exploratory
candidates, avoiding a queue dominated by one repeated headline/event.
"""
import argparse,json,re
from collections import Counter
from pathlib import Path

def review_queue(report,*,limit=60,high_fraction=.5,max_per_host_pair=10):
    if not 2<=limit<=200 or not 0<high_fraction<1:raise ValueError("Invalid queue budget")
    pairs=report.get("pairs",[])
    if not isinstance(pairs,list):raise ValueError("Invalid semantic report")
    # Preserve the frozen original rank in each review item.
    candidates=[]
    for rank,p in enumerate(pairs,1):
        a=p.get("left") or {};b=p.get("right") or {}
        if not a.get("url") or not b.get("url") or not a.get("title") or not b.get("title"):continue
        hosts=tuple(sorted([a.get("host",""),b.get("host","")]))
        candidates.append({"frozen_rank":rank,"similarity":p.get("similarity"),
                           "left":a,"right":b,"host_pair":hosts,
                           "review_status":"unreviewed",
                           "review_prompt":"Same event, related distinct events, shared context, or unsupported link?",
                           "epistemic_relation":"not_assessed"})
    selected=[];seen=set();host_count=Counter();doc_count=Counter()
    def add(c):
        key=(c["left"]["url"],c["right"]["url"])
        if key in seen or host_count[c["host_pair"]]>=max_per_host_pair:return False
        # Limit concentration around one prominent article.
        if doc_count[c["left"]["url"]]>=3 or doc_count[c["right"]["url"]]>=3:return False
        selected.append(c);seen.add(key);host_count[c["host_pair"]]+=1
        doc_count[c["left"]["url"]]+=1;doc_count[c["right"]["url"]]+=1
        return True
    for c in candidates:
        if len(selected)>=int(limit*high_fraction):break
        add(c)
    # Explore lower similarity neighborhoods instead of only easy duplicates.
    for c in reversed(candidates):
        if len(selected)>=limit:break
        add(c)
    selected.sort(key=lambda x:x["frozen_rank"])
    for c in selected:c["host_pair"]=list(c["host_pair"])
    return {"schema_version":1,"purpose":"balanced_manual_epistemic_review",
            "frozen_candidate_count":len(candidates),"selected":selected,
            "automatic_topic_creation":False,"automatic_publication":False,
            "limitations":["Selection is a heuristic, not a representative random precision estimate.",
                           "Review requires full source passages and claim-level evidence.",
                           "Original semantic rank is preserved; the retrieval model is unchanged."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("report",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=review_queue(json.loads(a.report.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"frozen_candidates":result["frozen_candidate_count"],
                      "review_items":len(result["selected"])}))
if __name__=="__main__":main()
