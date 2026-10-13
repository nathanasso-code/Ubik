"""Run the entire Ubik experimental analysis over real full-text inputs.

Lexical baseline, not LLM entailment. Conservative clustering and extractive
claim candidates; no truth verification, source independence or publication.
"""
import argparse,collections,json,math,re
from pathlib import Path
from ingestion.source_claim_candidates import claim_candidates

STOP={"the","and","with","from","after","that","this","into","over","under","for","have","has","was","were","are","its","their","said","says","will","about","more","than","new","news","world","wikinews"}
def terms(text):
    return {x for x in re.findall(r"[a-zà-ÿ]{4,}",text.lower()) if x not in STOP}
def similarity(a,b):
    if not a or not b:return 0.
    return len(a&b)/len(a|b)
def categorize(title,body):
    s=(title+" "+body[:1200]).lower()
    rules=[("Ambiente e clima",["hurricane","storm","flood","earthquake","climate","wildfire"]),
           ("Tecnologia e scienza",["research","scientists","study","software","internet","spacecraft","satellite"]),
           ("Salute",["hospital","disease","virus","vaccine","health"]),
           ("Economia",["economy","inflation","market","bank","trade"]),
           ("Politica e società",["election","government","parliament","minister","president"]),
           ("Conflitti e sicurezza",["attack","war","military","missile","bomb"])]
    counts=[(sum(s.count(word) for word in words),name) for name,words in rules]
    best=max(counts,default=(0,"Da classificare"))
    return best[1] if best[0]>=2 else "Da classificare"
def analyze(corpus,*,max_pairs=400):
    docs=corpus.get("documents",[])
    if not isinstance(docs,list):raise ValueError("Invalid corpus")
    sources={d["url"]:{"text":d["text"],"sha256":d["sha256"]} for d in docs}
    claims=claim_candidates(sources,max_per_source=5)
    claims_by_url={x["url"]:x["candidates"] for x in claims["sources"]}
    indexed=[terms(d["title"]) for d in docs]
    pairs=[]
    for i in range(len(docs)):
        for j in range(i+1,len(docs)):
            score=similarity(indexed[i],indexed[j])
            if score>=0.34 and len(indexed[i]&indexed[j])>=2:
                pairs.append((score,i,j))
    pairs.sort(reverse=True)
    # Strict complete-link-like selection: each added item must match all cluster members.
    groups=[];assigned=set()
    for score,i,j in pairs[:max_pairs]:
        if i in assigned or j in assigned:continue
        group=[i,j];assigned.update(group)
        for k in range(len(docs)):
            if k in assigned:continue
            if all(similarity(indexed[k],indexed[m])>=0.34 and len(indexed[k]&indexed[m])>=2 for m in group):
                group.append(k);assigned.add(k)
        groups.append(group)
    for i in range(len(docs)):
        if i not in assigned:groups.append([i])
    cards=[]
    for n,group in enumerate(groups):
        members=[docs[i] for i in group]
        categories=collections.Counter(categorize(d["title"],d["text"]) for d in members)
        category=categories.most_common(1)[0][0]
        # Syntheses are explicitly descriptive and do not repeat full text.
        if len(members)>1:
            summary="I documenti selezionati trattano argomenti potenzialmente collegati. " + "Il confronto puntuale delle affermazioni e della cronologia resta da verificare."
        else:
            summary="Documento acquisito per l'analisi delle affermazioni. Non sono stati trovati altri titoli sufficientemente simili nel campione."
        cards.append({"id":f"corpus-card-{n+1}","title":members[0]["title"],
                      "source_urls":[d["url"] for d in members],
                      "source_count":len(members),
                      "category":category,"category_method":"closed_lexical_baseline",
                      "synthesis_it":summary,
                      "claim_candidates":[{"url":d["url"],"count":len(claims_by_url.get(d["url"],[])),
                                           "quotes_available_for_private_review":bool(claims_by_url.get(d["url"]))} for d in members],
                      "cluster_status":"candidate_only" if len(group)>1 else "single_source",
                      "claims_verified":False,"same_event_verified":False,
                      "relation_verified":False,"published":False})
    return {"schema_version":1,"source":"full_article_body_corpus",
            "documents_acquired":len(docs),"documents_with_claim_candidates":sum(bool(claims_by_url.get(d["url"])) for d in docs),
            "claim_candidate_count":sum(len(v) for v in claims_by_url.values()),
            "title_similarity_pairs":len(pairs),"multi_source_candidate_clusters":sum(len(g)>1 for g in groups),
            "cards":cards,"claim_candidates":claims,
            "automatic_publication":False,
            "limitations":["Clustering and taxonomy use lexical baselines, not validated semantic inference.",
                           "Synthesis is a cautious template, not an event-specific generated account.",
                           "Sentence candidates are not verified claims or independent corroboration."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("corpus",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();r=analyze(json.loads(a.corpus.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    # Do not publish full extracted article bodies; outputs are research-only and
    # keep exact quotes in private artifacts, not public website.
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:r[k] for k in ("documents_acquired","claim_candidate_count","title_similarity_pairs","multi_source_candidate_clusters")}))
if __name__=="__main__":main()
