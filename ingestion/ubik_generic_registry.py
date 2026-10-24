"""Topic-agnostic deterministic identity candidate generator.
No LLM calls, no embeddings, no topic-specific grouping rules.
"""
import json, re, unicodedata
from pathlib import Path
from collections import defaultdict

ROOT=Path("data/taxonomy-pilot")
SOURCE=ROOT/"fact-reference-pilot.json"
TARGET=ROOT/"registry-matching-results.json"
# Lexical aliases describe entity identity or surface forms, not event identity.
ALIASES={
 "united states":"usa","u.s.":"usa","us":"usa","united states of america":"usa",
 "washington":"usa","u.s. government":"usa",
 "donald trump":"trump","president trump":"trump",
 "volodymyr zelenskyy":"zelensky","volodymyr zelensky":"zelensky",
 "russian federation":"russia","russian":"russia",
 "ukrainian":"ukraine",
}
STOP={"the","a","an","of","to","on","in","for","and","by","with","from","at","its","over","new"}
FIELDS=("type","actor","action","object","recipient","date","place")
def normalize(value):
 if value is None:return ""
 s=unicodedata.normalize("NFKC",str(value)).lower().strip()
 s=re.sub(r"[^\w\s-]"," ",s)
 s=" ".join(s.split())
 return ALIASES.get(s,s)
def tokens(value):
 s=normalize(value)
 return set(s.split())-STOP
def compare(a,b):
 details={}
 contradictions=[]
 supports=[]
 for field in FIELDS:
  x,y=normalize(a.get(field)),normalize(b.get(field))
  if not x or not y:
   details[field]="unknown";continue
  if x==y:
   details[field]="exact";supports.append(field);continue
  if field in ("date","place","recipient","actor","type"):
   details[field]="different"
   if field in ("date","place") or (field=="actor" and x not in y and y not in x):
    contradictions.append(field)
   continue
  tx,ty=tokens(x),tokens(y)
  overlap=len(tx&ty)/max(1,len(tx|ty))
  details[field]="partial" if overlap>=0.5 else "different"
  if overlap>=0.5:supports.append(field)
 ids_a={normalize(v) for v in (a.get("identifiers") or []) if v}
 ids_b={normalize(v) for v in (b.get("identifiers") or []) if v}
 if ids_a and ids_b and ids_a.isdisjoint(ids_b):contradictions.append("identifiers")
 if ids_a & ids_b:supports.append("identifiers")
 discriminators=sum(f in supports for f in ("actor","action","object","recipient","date","place","identifiers"))
 if contradictions:status="excluded"
 elif "identifiers" in supports or (discriminators>=4 and "action" in supports and "object" in supports):status="candidate_strong"
 elif discriminators>=2:status="candidate_weak"
 else:status="indeterminate"
 # Strong is not confirmed identity; independent evidence is required.
 return {"status":status,"details":details,"supports":supports,"contradictions":contradictions}
def main():
 data=json.loads(SOURCE.read_text())
 nodes=[]
 for item in data["items"]:
  extraction=item["extraction"]
  nodes.append({"id":item["key"]+":fact","news_key":item["key"],"kind":"fact","data":extraction["fact"],"title":item["title"]})
  for i,ref in enumerate(extraction["references"]):
   nodes.append({"id":item["key"]+":ref"+str(i),"news_key":item["key"],"kind":"reference","data":ref,"title":item["title"]})
 edges=[]
 for i,a in enumerate(nodes):
  for b in nodes[i+1:]:
   if a["news_key"]==b["news_key"]:continue
   # Explicitly record all comparisons, even excluded ones, for auditability.
   verdict=compare(a["data"],b["data"])
   if verdict["status"] in ("candidate_strong","candidate_weak"):
    edges.append({"a":a["id"],"b":b["id"],**verdict})
 summary={"news":len(data["items"]),"nodes":len(nodes),"candidate_strong":sum(e["status"]=="candidate_strong" for e in edges),"candidate_weak":sum(e["status"]=="candidate_weak" for e in edges),"confirmed":0,"note":"Candidate pairs are NOT merged. No topic-specific exceptions."}
 TARGET.write_text(json.dumps({"summary":summary,"nodes":nodes,"edges":edges,"aliases":ALIASES},ensure_ascii=False,indent=2))
 print(json.dumps(summary))
if __name__=="__main__":main()
