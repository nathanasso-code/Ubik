"""Dependency-free semantic-proxy candidate discovery with token-normalized concepts.

This is a lexical-concept proxy, NOT neural embeddings. It is deliberately
labeled to prevent claims of semantic model coverage without a model.
"""
import argparse,json,re,collections
from pathlib import Path
from urllib.parse import urlsplit
from ingestion.cross_source_candidate_mining import build,tokens

# Bounded, auditable concept normalization; useful to probe lexical gaps.
CONCEPTS={
 "injured":"injury","wounded":"injury","hurt":"injury","hospitalized":"injury",
 "attacked":"attack","assaulted":"attack","assault":"attack","aggression":"attack",
 "journalist":"reporter","photojournalist":"reporter","photographer":"reporter",
 "settlers":"settler","settler":"settler",
 "protesters":"protest","protests":"protest","demonstrators":"protest",
 "banned":"ban","prohibited":"ban","outlawed":"ban",
 "sold":"sale","selling":"sale","sales":"sale",
 "killed":"death","dead":"death","fatalities":"death",
 "fired":"dismissal","dismissed":"dismissal","sacked":"dismissal",
 "election":"vote","voting":"vote","ballot":"vote",
}
def concepts(s):
    # Restrict the probe to explicit curated equivalences; shared generic words
    # alone cannot create candidate edges.
    return set(CONCEPTS[t] for t in tokens(s) if t in CONCEPTS)
def candidate_pairs(rows,baseline,top_k=5000):
    docs={r["url"]:r for r in rows if r.get("url") and r.get("title")}
    baseline_keys={tuple(sorted((p["left"]["url"],p["right"]["url"]))) for p in baseline["top_pairs"]}
    inverted=collections.defaultdict(list)
    for url,row in docs.items():
        for concept in concepts(row.get("title","")+" "+str(row.get("description") or "")):
            inverted[concept].append(url)
    overlap=collections.Counter()
    for term,urls in inverted.items():
        if len(urls)>120:continue
        for i,a in enumerate(urls):
            for b in urls[i+1:]:
                if urlsplit(a).hostname==urlsplit(b).hostname:continue
                overlap[tuple(sorted((a,b)))]+=1
    ranked=sorted(((pair,n) for pair,n in overlap.items() if n>=2),key=lambda x:(-x[1],x[0]))
    novel=[]
    for (a,b),shared in ranked:
        if (a,b) in baseline_keys:continue
        novel.append({"left":{"url":a,"title":docs[a]["title"],"publisher":docs[a].get("publisher")},
                      "right":{"url":b,"title":docs[b]["title"],"publisher":docs[b].get("publisher")},
                      "shared_concept_count":shared,"status":"unreviewed"})
        if len(novel)>=top_k:break
    return {"schema_version":1,"method":"auditable_concept_normalization_proxy_not_embeddings",
            "corpus_documents":len(docs),"baseline_pairs":len(baseline_keys),
            "novel_candidate_pairs":len(novel),"candidates":novel,
            "limitations":["Curated equivalences require at least two independent matching concepts; this is not semantic embeddings.",
                           "Novel means absent from bounded baseline top-k, not semantically novel.",
                           "Candidates require article-text event identity review."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path)
    p.add_argument("baseline",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--top-k",type=int,default=100)
    a=p.parse_args()
    rows=json.loads(a.input.read_text())["items"]
    baseline=json.loads(a.baseline.read_text())
    result=candidate_pairs(rows,baseline,top_k=min(5000,max(1,a.top_k)))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Concept candidate probe:",json.dumps({"corpus_documents":result["corpus_documents"],"baseline_pairs":result["baseline_pairs"],"novel_candidate_pairs":result["novel_candidate_pairs"]}))
if __name__=="__main__":main()
