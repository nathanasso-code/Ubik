"""Source-grounded statement comparison pilot.

Extracts title and feed-description sentences, retrieves candidate statement
pairs within existing document edges, and optionally scores multilingual NLI.
NLI labels describe textual entailment, not truth or event identity.
"""
import argparse,json,re
from pathlib import Path
from ingestion.semantic_topic_neighbor_pilot import extract
from ingestion.grounded_extractive_briefs import sentences
from ingestion.statement_event_graph import statement

def claims(doc,limit=3):
 candidates=[("title",doc["title"])]
 candidates.extend(("description",s) for s in sentences(doc.get("description") or ""))
 seen=set();out=[]
 for location,s in candidates:
  s=re.sub(r"\s+"," ",s).strip()
  if len(s)<20 or s.casefold() in seen:continue
  seen.add(s.casefold())
  out.append({"text":s[:450],"source_url":doc["url"],"source_id":doc.get("source_id"),
              "evidence_location":location,"extraction_method":"sentence_candidate_not_verified"})
  if len(out)>=limit:break
 return out

def lexical_overlap(a,b):
 t=lambda s:set(re.findall(r"[^\W\d_]{3,}",s.casefold(),re.UNICODE))
 x,y=t(a),t(b)
 return len(x&y)/max(1,len(x|y))

def compare(snapshot,hybrid,predict=None,max_pairs=100):
 docs={d["url"]:d for d in extract(snapshot,10000)}
 edges=[];nli_calls=0
 for p in hybrid.get("pairs",[])[:max_pairs]:
  a,b=docs.get(p["url_a"]),docs.get(p["url_b"])
  if not a or not b:continue
  ca,cb=claims(a),claims(b)
  ranked=sorted(((lexical_overlap(x["text"],y["text"]),x,y) for x in ca for y in cb),
                key=lambda z:-z[0])[:2]
  comparisons=[]
  for overlap,x,y in ranked:
   item={"statement_a":x,"statement_b":y,"lexical_overlap":round(overlap,4),
         "relation":"not_assessed","review_status":"unreviewed"}
   if predict is not None:
    forward=predict(x["text"],y["text"])
    backward=predict(y["text"],x["text"])
    nli_calls+=2
    item["directional_nli"]={"a_to_b":forward,"b_to_a":backward}
    # Directionality is essential: a single entailment is not equivalence.
    la,lb=forward["label"],backward["label"]
    if la=="contradiction" and lb=="contradiction":item["relation"]="model_contradiction_candidate"
    elif la=="entailment" and lb=="entailment":item["relation"]="model_equivalence_candidate"
    elif la=="entailment" or lb=="entailment":item["relation"]="model_directional_entailment_candidate"
    else:item["relation"]="model_neutral_or_uncertain"
   comparisons.append(item)
  edges.append({"url_a":a["url"],"url_b":b["url"],"hybrid_decision":p.get("decision"),
                "comparisons":comparisons,"event_identity":"not_verified"})
 return {"schema_version":1,"method":"directional_nli_review" if predict else "lexical_statement_baseline",
         "edges":edges,"coverage":{"document_pairs":len(edges),
          "statement_pairs":sum(len(x["comparisons"]) for x in edges),"nli_calls":nli_calls},
         "limitations":["Feed description/title sentences are candidates, not independently verified claims.",
           "NLI compares textual meaning, not factual truth or source credibility.",
           "Neutral predictions do not establish absence of a relation.",
           "Contradiction and entailment scores require human gold-label calibration.",
           "Same-event identity is separate from statement-level inference.",
           "Texts may be truncated feed descriptions; no protected full text is copied."]}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--snapshot",type=Path,required=True)
 p.add_argument("--hybrid",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True)
 p.add_argument("--max-pairs",type=int,default=50)
 p.add_argument("--model",default="")
 a=p.parse_args()
 predict=None
 if a.model:
  from transformers import pipeline
  classifier=pipeline("text-classification",model=a.model,device=-1)
  def predict(x,y):
   result=classifier({"text":x,"text_pair":y},truncation=True)
   if isinstance(result,list):
    if not result:raise ValueError("Empty NLI prediction")
    result=result[0]
   if not isinstance(result,dict) or "label" not in result or "score" not in result:
    raise ValueError("Unexpected NLI prediction shape")
   label=str(result["label"]).lower()
   # Unknown label mappings must never silently become entailment.
   if label not in ("entailment","neutral","contradiction"):label="unknown:"+label
   return {"label":label,"score":round(float(result["score"]),4)}
 payload=compare(json.loads(a.snapshot.read_text()),json.loads(a.hybrid.read_text()),predict,a.max_pairs)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(payload["coverage"]))
if __name__=="__main__":main()
