"""Auditable RSS excerpt candidates: not full article bodies or verified claims."""
import argparse,collections,hashlib,json,re
from pathlib import Path

def audit(snapshot,pairs=None,max_examples=100):
    rows=snapshot.get("items",[])
    unique={}
    for row in rows:
        u=row.get("url","")
        if u.startswith("https://") and u not in unique:unique[u]=row
    docs=list(unique.values())
    counts=collections.Counter(x.get("source_id","unknown") for x in docs)
    described=[x for x in docs if len(x.get("description") or "")>=60]
    excerpts=[]
    for x in described:
        raw=" ".join(x["description"].split())
        for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9“])',raw):
            if 45<=len(sentence)<=450:
                excerpts.append({"url":x["url"],"source_id":x.get("source_id"),
                  "excerpt":sentence,"excerpt_sha256":hashlib.sha256(sentence.encode()).hexdigest(),
                  "evidence_kind":"rss_publisher_description","verified":False,
                  "source_body_acquired":False})
                break
    pairrows=(pairs or {}).get("pairs",[])
    links=[]
    for p in pairrows[:max_examples]:
        a=p.get("left",{});b=p.get("right",{})
        if a.get("url") not in unique or b.get("url") not in unique:continue
        links.append({"left_url":a["url"],"right_url":b["url"],
          "similarity":p.get("similarity"),"relation":"semantic_neighbor_unverified",
          "left_has_rss_excerpt":len(unique[a["url"]].get("description") or "")>=60,
          "right_has_rss_excerpt":len(unique[b["url"]].get("description") or "")>=60,
          "same_event_verified":False,"independent_corroboration_verified":False})
    return {"schema_version":1,"purpose":"large_scale_rss_excerpt_evidence_audit",
      "coverage":{"rss_observations":len(rows),"distinct_urls":len(docs),
       "sources_with_distinct_urls":len(counts),"documents_with_substantial_rss_description":len(described),
       "extracted_description_sentence_candidates":len(excerpts),"semantic_pairs_available":len(pairrows),
       "semantic_pairs_reviewed_as_candidates":len(links),"full_article_bodies_acquired":0,
       "claims_verified":0},"source_counts":dict(counts),
       "excerpt_candidates":excerpts,"relation_candidates":links,
       "limitations":["RSS descriptions are not complete article bodies.",
        "A sentence candidate is not an atomic fact or an independently verified assertion.",
        "Similarity cannot establish event identity, agreement or contradiction.",
        "Syndicated agency reporting is not independent corroboration."],
       "publication_approved":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("rss",type=Path)
    p.add_argument("--pairs",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=audit(json.loads(a.rss.read_text()),json.loads(a.pairs.read_text()) if a.pairs and a.pairs.exists() else None)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(d["coverage"]))
if __name__=="__main__":main()
