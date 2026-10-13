"""Review-only hybrid event pairing. No automatic merges."""
import argparse, json, re, math
from pathlib import Path
from datetime import datetime, timezone
from ingestion.semantic_topic_neighbor_pilot import analyze, extract
from ingestion.semantic_topic_router import MODEL
STOP=set("the and for with from this that have into after over about said says will were their a an of to in on at as by is are was be it its new not".split())
def terms(text):
 return set(x for x in re.findall(r"[^\W\d_]{3,}",text.casefold(),re.UNICODE) if x not in STOP)
def tokens(text):
 return set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b",text))
def day(doc):
 value=next((doc.get(k) for k in ("published_at","published","date","pub_date") if doc.get(k)),None)
 if not value:return None
 try:return datetime.fromisoformat(str(value).replace("Z","+00:00")).date()
 except ValueError:return None
def compare(a,b,similarity):
 ta,tb=terms(a["title"]),terms(b["title"])
 overlap=len(ta&tb)/max(1,len(ta|tb))
 ea,eb=tokens(a["title"]),tokens(b["title"])
 entities=len(ea&eb)/max(1,len(ea|eb)) if ea and eb else None
 da,db=day(a),day(b)
 gap=abs((da-db).days) if da and db else None
 # Ranking score, not a calibrated event probability.
 score=.65*similarity+.25*overlap+.10*(entities if entities is not None else 0)
 if gap is not None and gap>7:score-=min(.25,(gap-7)*.01)
 if similarity<.76 or score<.67:
  decision="related_topic_or_unresolved"
 elif overlap>=.25 and (gap is None or gap<=7):
  decision="same_event_review_candidate"
 else:
  decision="related_topic_or_unresolved"
 return {"semantic_similarity":round(similarity,4),"title_jaccard":round(overlap,4),
 "capitalized_phrase_overlap":round(entities,4) if entities is not None else None,
 "publication_gap_days":gap,"hybrid_score":round(score,4),"decision":decision,
 "note":"Heuristic candidate only; title-case phrases are not reliable NER"}
def run(snapshot,embed,limit=400):
 baseline=analyze(snapshot,embed,limit)
 docs=baseline["documents"]
 byurl={d["url"]:d for d in docs}
 # Use baseline semantic nearest-neighbor pool; avoid introducing additional embedding inference.
 pairs=[]
 for item in baseline["cross_source_neighbors"]:
  a,b=byurl[item["url_a"]],byurl[item["url_b"]]
  result=compare(a,b,item["similarity"])
  pairs.append({"url_a":a["url"],"title_a":a["title"],"url_b":b["url"],"title_b":b["title"],**result})
 return {"schema_version":1,"model":MODEL,"taxonomy":baseline["coverage"],
  "documents":docs,"pairs":pairs,
  "coverage":{"candidate_pairs":len(pairs),"same_event_review_candidates":sum(p["decision"]=="same_event_review_candidate" for p in pairs),
  "unresolved":sum(p["decision"]!="same_event_review_candidate" for p in pairs)},
  "limitations":["Only top 100 semantic neighbor pairs are considered, not all possible pairs.",
  "Title-only lexical overlap and capitalization are weak proxies; multilingual matches may be missed.",
  "Publication dates are absent unless provided by the input snapshot and preserved upstream.",
  "Scores and thresholds are uncalibrated; no automatic merges or event identity assertions.",
  "No gold-labeled evaluation has been performed."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--snapshot",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--limit",type=int,default=400);a=p.parse_args()
 from sentence_transformers import SentenceTransformer
 model=SentenceTransformer(MODEL)
 payload=run(json.loads(a.snapshot.read_text()),lambda xs:model.encode(xs,batch_size=32,normalize_embeddings=True).tolist(),a.limit)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(payload["coverage"]))
if __name__=="__main__":main()
