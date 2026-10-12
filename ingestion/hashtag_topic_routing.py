"""Contextual hashtag-to-topic suggestions with provenance and abstention.

Character n-gram TF-IDF similarity handles related morphological variants,
not true multilingual semantic inference. No LLM or embedding service is used.
"""
import argparse,json,math,re
from collections import Counter,defaultdict
from pathlib import Path

def features(text):
    words=re.findall(r"[^\W_]+",str(text or "").casefold(),re.UNICODE)
    return Counter("c:"+w[i:i+4] for w in words if len(w)>=5 for i in range(len(w)-3))

def similarity(a,b,idf):
    numerator=sum(v*b.get(k,0)*idf.get(k,1)**2 for k,v in a.items())
    def norm(x):return math.sqrt(sum((v*idf.get(k,1))**2 for k,v in x.items()))
    den=norm(a)*norm(b)
    return numerator/den if den else 0

def topic_index(catalog,registry=None):
    topics=list(catalog.get("topics",[]))
    for t in (registry or []):
        if t.get("id") not in {x["id"] for x in topics}:
            topics.append(t)
    return [{"id":t["id"],"title":t["title"],
             "context":" ".join([t.get("title",""),t.get("description",""),
                                 *t.get("questions",[]),*t.get("semantic_context",[])])}
            for t in topics if t.get("id") and t.get("title")]

def suggest_hashtag_topics(social_records,topics,*,min_posts=2,min_accounts=2,min_score=0.12,max_suggestions=100):
    if not 1<=min_posts<=30 or not 1<=min_accounts<=30 or not 0<min_score<1:
        raise ValueError("Invalid matching budget")
    tags=defaultdict(lambda:{"posts":set(),"accounts":set(),"contexts":[],"links":set()})
    for record in social_records:
        meta=record.get("metadata") or {}
        for raw in set(meta.get("hashtags") or []):
            if not isinstance(raw,str):continue
            tag=raw.lstrip("#").casefold()
            if not 3<=len(tag)<=64:continue
            group=tags[tag]
            group["posts"].add(record.get("url",""))
            group["accounts"].add(record.get("source_id",""))
            group["contexts"].append((meta.get("text_preview") or record.get("title") or "")[:500])
            group["links"].update(meta.get("linked_documents") or [])
    topic_features={t["id"]:features(t["context"]) for t in topics}
    eligible={tag:group for tag,group in tags.items()
              if len(group["posts"])>=min_posts and len(group["accounts"])>=min_accounts}
    contexts={tag:features(tag+" "+" ".join(group["contexts"][:15])) for tag,group in eligible.items()}
    df=Counter(k for vector in list(topic_features.values())+list(contexts.values()) for k in vector)
    n=len(topic_features)+len(contexts)
    idf={k:math.log((n+1)/(v+1))+1 for k,v in df.items()}
    results=[]
    for tag,group in eligible.items():
        ranked=sorted(((similarity(contexts[tag],topic_features[t["id"]],idf),t)
                       for t in topics),key=lambda x:-x[0])
        for score,t in ranked[:3]:
            if score<min_score:continue
            results.append({"hashtag":tag,"topic_id":t["id"],"topic_title":t["title"],
                            "contextual_similarity":round(score,4),
                            "observed_posts":len(group["posts"]),
                            "observed_accounts_unverified":len(group["accounts"]),
                            "supporting_posts":sorted(group["posts"])[:12],
                            "linked_document_hints":sorted(group["links"])[:12],
                            "basis":"observed_hashtag_and_post_context_char_ngram_tfidf",
                            "status":"semantic_review_candidate_not_validated"})
    results.sort(key=lambda x:(-x["contextual_similarity"],-x["observed_posts"],x["hashtag"]))
    return {"schema_version":1,"purpose":"hashtag_topic_contextual_routing",
            "topics_considered":len(topics),"hashtags_observed":len(tags),
            "hashtags_eligible":len(eligible),"suggestions":results[:max_suggestions],
            "unassigned_hashtags":sorted(set(eligible)-{x["hashtag"] for x in results}),
            "automatic_topic_assignment":False,
            "limitations":["Character n-grams are contextual lexical matching, not multilingual embeddings.",
                           "Semantic matches must be manually evaluated for false positives.",
                           "Hashtags without enough observed independent-looking accounts abstain.",
                           "Observed accounts may be bots or bridged copies.",
                           "Only post text and links present in supplied snapshots are considered."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--social",type=Path,required=True)
    p.add_argument("--catalog",type=Path,default=Path("data/catalog.json"))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    payload=json.loads(a.social.read_text(encoding="utf-8"))
    # A topic-social summary contains aggregated URL hints, not full post text:
    # require a raw observation snapshot to avoid pretending to have context.
    if not isinstance(payload.get("observations"),list):
        raise SystemExit("Require raw social observations with hashtags and post context")
    result=suggest_hashtag_topics(payload["observations"],topic_index(json.loads(a.catalog.read_text(encoding="utf-8"))))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"suggestions":len(result["suggestions"]),
                      "eligible_hashtags":result["hashtags_eligible"]}))
if __name__=="__main__":main()
