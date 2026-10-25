"""Frozen phase-1 embedding retrieval evaluation; no LLM, no threshold fitting."""
import json,itertools,os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

root=Path("data/taxonomy-pilot")
data=json.loads((root/"v4-sonnet55.json").read_text())
events=[e for source in data["sources"] for e in source["events"]]
assert len(events)==33
ids=[e["qualified_id"] for e in events]
texts=["passage: "+str(e.get("action") or "").strip()+" "+str(e.get("object") or "").strip() for e in events]
model=SentenceTransformer("intfloat/multilingual-e5-small",device="cpu")
vec=model.encode(texts,normalize_embeddings=True,convert_to_numpy=True,show_progress_bar=False)
S=vec@vec.T
groups={
"A":["S188:E2","S382:E5","S383:E2","S387:E2","S389:E4","S433:E4"],
"B":["S188:E1","S383:E1","S433:E1","S465:E2"],
"C":["S382:E1","S387:E4"],
"A2":["S408:E4","S433:E3"]}
positive={frozenset(pair) for group in groups.values() for pair in itertools.combinations(group,2)}
positive_without_C={p for p in positive if p!=frozenset(groups["C"])}
ab={frozenset((a,b)) for a in groups["A"] for b in groups["B"]}
cross_ab={p for p in ab if len({x.split(":")[0] for x in p})==2}
assert len(positive)==23 and len(ab)==24 and len(cross_ab)==21
idx={key:i for i,key in enumerate(ids)}
def value(pair):
 a,b=tuple(pair)
 return float(S[idx[a],idx[b]])
def distribution(pos,neg):
 ps=[value(p) for p in pos];ns=[value(p) for p in neg]
 wins=sum((p>n)+0.5*(p==n) for p in ps for n in ns)
 return {"min_positive":min(ps),"max_negative":max(ns),"margin":min(ps)-max(ns),
         "positive_at_or_below_max_negative":sum(p<=max(ns) for p in ps),
         "ordered_fraction":wins/(len(ps)*len(ns))}
def recall(k):
 hit=total=0
 per_event=[]
 for key in ids:
  truth={next(iter(p-{key})) for p in positive if key in p}
  if not truth:continue
  ranks=sorted((other for other in ids if other!=key and other.split(":")[0]!=key.split(":")[0]),
   key=lambda other:-float(S[idx[key],idx[other]]))[:k]
  n=len(truth & set(ranks));hit+=n;total+=len(truth)
  per_event.append({"event":key,"hits":n,"total":len(truth),"candidates":ranks})
 return {"hits":hit,"total":total,"recall":hit/total,"per_event":per_event}
excluded={frozenset(("S433:E2","S465:E1"))}
uncertain="S408:E6"
other_neg=[frozenset((a,b)) for a,b in itertools.combinations(ids,2)
 if a.split(":")[0]!=b.split(":")[0] and frozenset((a,b)) not in positive
 and frozenset((a,b)) not in ab and frozenset((a,b)) not in excluded
 and uncertain not in (a,b)]
worst_positive=sorted(({"pair":sorted(p),"score":value(p)} for p in positive),key=lambda x:x["score"])[:7]
worst_ab=sorted(({"pair":sorted(p),"score":value(p)} for p in ab),key=lambda x:-x["score"])[:7]
out={"method":"intfloat/multilingual-e5-small","canonical_description":"passage: {action} {object}",
 "events":len(events),"positive_pairs":len(positive),"AB_pairs":len(ab),"AB_cross_source_pairs":len(cross_ab),
 "with_C":distribution(positive,ab),"without_C":distribution(positive_without_C,ab),
 "AB_cross_source":distribution(positive,cross_ab),"recall_at_3":recall(3),"recall_at_5":recall(5),
 "other_negative_pairs":len(other_neg),"other_negative_above_min_positive":sum(value(p)>=min(map(value,positive)) for p in other_neg),
 "lowest_positive_pairs":worst_positive,"highest_AB_pairs":worst_ab,
 "S387_E2_ranking":sorted(({"event":other,"score":float(S[idx["S387:E2"],idx[other]])}
 for other in ids if other!="S387:E2" and other.split(":")[0]!="S387"),key=lambda x:-x["score"])[:12]}
root.mkdir(parents=True,exist_ok=True)
(root/"phase1-embedding-e5-small.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in out.items() if k in ("method","events","with_C","without_C","AB_cross_source","other_negative_pairs")},ensure_ascii=False))
