"""Grounded extractive briefing from review-only event candidates.

No generative paraphrase: each selected sentence retains its original source URL.
"""
import argparse,json,re
from pathlib import Path
from ingestion.semantic_topic_neighbor_pilot import extract
def sentences(text):
 return [s.strip() for s in re.split(r"(?<=[.!?])\s+",text) if len(s.strip())>=35]
def tokens(text):
 return set(re.findall(r"[^\W\d_]{4,}",text.casefold(),re.UNICODE))
def brief(snapshot,hybrid,limit=25):
 docs={x["url"]:x for x in extract(snapshot,10000)}
 groups=[]
 for pair in hybrid.get("pairs",[]):
  if pair.get("decision")!="same_event_review_candidate":continue
  selected=[]
  for key in ("url_a","url_b"):
   url=pair[key];doc=docs.get(url)
   if not doc:continue
   candidates=sentences(doc.get("description") or "")
   if not candidates:continue
   best=max(candidates,key=lambda s:len(tokens(s)&tokens(doc["title"])))
   if any(len(tokens(best)&tokens(x["text"]))/max(1,len(tokens(best)|tokens(x["text"])))>.78 for x in selected):continue
   selected.append({"text":best[:450],"url":url,"source_id":doc.get("source_id"),"kind":"verbatim_source_excerpt"})
  if not selected:continue
  groups.append({"title":docs.get(pair["url_a"],{}).get("title",""),"source_urls":[pair["url_a"],pair["url_b"]],
    "event_identity":"not_verified","brief_type":"extractive_preview_not_synthesis",
    "source_excerpts":selected,"missing_information":["Full-text access and cross-source event identity not established"]})
  if len(groups)>=limit:break
 return {"schema_version":1,"briefs":groups,"coverage":{"briefs":len(groups)},
 "limitations":["Extractive previews are not final Ubik syntheses.",
 "Excerpts come from feed descriptions, not necessarily article bodies.",
 "No factual validation or automatic publication.",
 "Copyright and reuse permissions must be checked before displaying excerpts publicly."]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--snapshot",type=Path,required=True);p.add_argument("--hybrid",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 payload=brief(json.loads(a.snapshot.read_text()),json.loads(a.hybrid.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(payload["coverage"]))
if __name__=="__main__":main()
