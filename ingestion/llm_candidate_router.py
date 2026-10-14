"""Route preselected article pairs to a bounded, review-only LLM queue.

Consumes existing hybrid event candidates. No external API is called.
"""
import argparse,json,hashlib
from pathlib import Path

def route(hybrid,budget=30):
    pairs=hybrid.get("pairs",[])
    candidates=[]
    for pair in pairs:
        a,b=pair.get("url_a"),pair.get("url_b")
        if not a or not b or a==b:continue
        similarity=float(pair.get("semantic_similarity",0))
        if similarity<0.70:continue
        lexical=float(pair.get("title_jaccard",0))
        gap=pair.get("publication_gap_days")
        uncertain=pair.get("decision")!="same_event_review_candidate"
        # Rank informative ambiguities, not simply duplicates. Not a calibrated probability.
        score=similarity+(.12 if uncertain else 0)+(.08 if lexical<.20 else 0)
        if gap is not None and 1<=gap<=30:score+=.05
        key=hashlib.sha256("|".join(sorted((a,b))).encode()).hexdigest()[:16]
        candidates.append({"pair_id":key,"url_a":a,"url_b":b,"title_a":pair.get("title_a",""),
           "title_b":pair.get("title_b",""),"selection_score":round(score,4),
           "selection_reason":"semantic_ambiguity" if uncertain else "same_event_candidate",
           "source_semantic_similarity":similarity,"requires_llm":True,
           "status":"queued_not_analyzed"})
    candidates.sort(key=lambda p:(-p["selection_score"],p["pair_id"]))
    selected=[];seen=set()
    for pair in candidates:
        if pair["pair_id"] in seen:continue
        seen.add(pair["pair_id"]);selected.append(pair)
        if len(selected)>=max(0,budget):break
    if budget<=0:selected=[]
    return {"schema_version":1,"selection_method":"hybrid_embedding_review_budget",
      "queue":selected,"coverage":{"input_pairs":len(pairs),"eligible_pairs":len(seen) if budget<=0 else len({p["pair_id"] for p in candidates}),
       "queued_pairs":len(selected),"budget":budget},
      "limitations":["Ranking is heuristic and not a calibrated relevance measure.",
       "No LLM was called and no category or relation was inferred.",
       "Candidates excluded by the embedding shortlist are not recoverable here.",
       "Novel isolated articles need a separate exploration lane."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--hybrid",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True);p.add_argument("--budget",type=int,default=30)
 a=p.parse_args();result=route(json.loads(a.hybrid.read_text()),a.budget)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
