"""Review-only event/statement graph over real RSS descriptions.

The graph preserves provenance and distinguishes event identity from statement
compatibility. No NLI, factual verification or automatic publication.
"""
import argparse,json,re
from collections import defaultdict
from pathlib import Path
from ingestion.semantic_topic_neighbor_pilot import extract
from ingestion.hybrid_event_review import terms,day

NEG=re.compile(r"\b(no|not|never|without|denies?|denied|false|failed|non|nessun[oa]?|senza|nega|smentisce)\b",re.I)
FUTURE=re.compile(r"\b(will|plans?|planned|expected|set to|to undergo|tomorrow|prevede|previsto|sarà|dovrà)\b",re.I)
PAST=re.compile(r"\b(was|were|has|had|underwent|confirmed|announced|sentenced|è stato|ha avuto|avvenuto)\b",re.I)
def statement(doc):
 title=doc.get("title","").strip()
 return {"text":title,"source_url":doc["url"],"source_id":doc.get("source_id"),
 "evidence_location":"title","negated":bool(NEG.search(title)),
 "future_marker":bool(FUTURE.search(title)),"past_marker":bool(PAST.search(title)),
 "extraction_method":"title_surface_features_only"}
def classify_pair(pair,docs):
 a,b=docs.get(pair["url_a"]),docs.get(pair["url_b"])
 if not a or not b:return None
 sa,sb=statement(a),statement(b)
 shared=terms(sa["text"])&terms(sb["text"])
 reasons=[]
 if sa["future_marker"]!=sb["future_marker"] and (sa["past_marker"] or sb["past_marker"]):
  reasons.append("temporal_modality_mismatch")
 if sa["negated"]!=sb["negated"] and len(shared)>=3:
  reasons.append("negation_mismatch_requires_scope_review")
 da,db=day(a),day(b)
 if da and db and abs((da-db).days)>7:reasons.append("publication_dates_over_seven_days_apart")
 decision=pair.get("decision")
 relation="candidate_same_event" if decision=="same_event_review_candidate" else "related_or_unresolved"
 if reasons:relation="needs_statement_level_review"
 return {"url_a":a["url"],"url_b":b["url"],"relation":relation,
 "flags":reasons,"shared_title_terms":sorted(shared)[:15],
 "hybrid_score":pair.get("hybrid_score"),"semantic_similarity":pair.get("semantic_similarity"),
 "provenance":[sa,sb],"review_status":"unreviewed"}
def graph(snapshot,hybrid):
 docs={d["url"]:d for d in extract(snapshot,10000)}
 links=[x for p in hybrid.get("pairs",[]) if (x:=classify_pair(p,docs))]
 # Conservative complete-link grouping: every cross-source pair in a proposed
 # cluster must be present and unflagged. No transitive chaining.
 eligible={frozenset((x["url_a"],x["url_b"])):x for x in links if x["relation"]=="candidate_same_event"}
 groups=[{u} for u in sorted({u for pair in eligible for u in pair})]
 changed=True
 while changed:
  changed=False
  for i in range(len(groups)):
   if changed:break
   for j in range(i+1,len(groups)):
    if all(frozenset((a,b)) in eligible for a in groups[i] for b in groups[j]):
     groups[i]|=groups[j];groups.pop(j);changed=True;break
 groups=sorted(groups,key=lambda g:(-len(g),sorted(g)[0]))
 return {"schema_version":1,"graph_type":"provenance_grounded_review_candidates",
 "nodes":[{"url":d["url"],"title":d["title"],"source_id":d.get("source_id"),
 "published_at":d.get("published_at"),"statement":statement(d)} for d in docs.values()],
 "edges":links,
 "complete_link_review_groups":[{"group_id":i+1,"urls":sorted(g),"status":"candidate_not_verified"} for i,g in enumerate(groups) if len(g)>1],
 "coverage":{"documents":len(docs),"edges":len(links),
 "statement_review_flags":sum(bool(x["flags"]) for x in links),
 "candidate_edges":len(eligible),"complete_link_groups":sum(len(g)>1 for g in groups)},
 "limitations":["Title-level polarity and temporal cues are not scoped natural-language inference.",
 "Negation mismatch is not proof of contradiction; tense mismatch is not proof of different events.",
 "Only the hybrid top-100 candidate pool is considered; missing edges can split true clusters.",
 "Complete-link groups are review candidates, not verified events or automatic merges.",
 "Descriptions/full texts must be assessed before asserting statement equivalence or disagreement."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--snapshot",type=Path,required=True);p.add_argument("--hybrid",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 result=graph(json.loads(a.snapshot.read_text()),json.loads(a.hybrid.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
