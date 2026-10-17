"""Metadata-first candidate retrieval. NO semantic auto-merge or publication.

Input: JSON list or {items:[{url,title,description,publisher,published_at,...}]}.
Outputs candidate edges and connected review contexts, preserving every source.
"""
import argparse,collections,datetime,json,math,re
from pathlib import Path
from urllib.parse import urlsplit

STOP=set("the a an and or of in on at to for from with as by is are was were that this it its after over amid new says say about into while how why what who has have had will can not de la le el di del della il lo gli una un per con su da e che dei delle al alla nel nella".split())
TOKEN=re.compile(r"[^\W_]+",re.UNICODE)

def terms(s):
    return [w for w in TOKEN.findall((s or "").casefold()) if len(w)>2 and w not in STOP and not w.isdigit()]

def published(d):
    for k in ("published_at","published","date","pub_date","publishedAt"):
        s=str(d.get(k) or "")
        if s:
            try:return datetime.date.fromisoformat(s[:10])
            except ValueError:pass
    return None

def retrieve(rows,threshold=0.42,top_per_source=8,max_day_gap=7):
    byurl={}
    for d in rows:
        if not isinstance(d,dict) or not d.get("url") or not d.get("title"):continue
        url=d["url"].split("#")[0]
        if url not in byurl or len(str(d.get("description") or ""))>len(str(byurl[url].get("description") or "")):
            byurl[url]={**d,"url":url}
    docs=[{"id":f"S{i+1}","url":u,"title":d["title"],"description":d.get("description") or "",
           "publisher":d.get("publisher"),"published_at":str(published(d) or "")}
          for i,(u,d) in enumerate(sorted(byurl.items()))]
    corpus=[terms(d["title"])*2+terms(d["description"])[:70] for d in docs]
    df=collections.Counter(w for toks in corpus for w in set(toks))
    vectors=[];postings=collections.defaultdict(list)
    for i,toks in enumerate(corpus):
        counts=collections.Counter(toks)
        vec={w:(1+math.log(n))*(1+math.log((len(docs)+1)/(df[w]+1))) for w,n in counts.items()}
        norm=math.sqrt(sum(x*x for x in vec.values())) or 1
        vec={w:x/norm for w,x in vec.items()}
        vectors.append(vec)
        for w in vec:postings[w].append(i)
    edges={}
    for i,d in enumerate(docs):
        candidates=collections.Counter()
        for w,weight in vectors[i].items():
            if df[w]>max(60,len(docs)//5):continue
            for j in postings[w]:
                if j<=i:continue
                candidates[j]+=weight*vectors[j][w]
        ranked=[]
        for j,score in candidates.items():
            a=published(d);b=published(docs[j])
            if a and b and abs((a-b).days)>max_day_gap:continue
            if score<threshold:continue
            host_a=urlsplit(d["url"]).hostname or "";host_b=urlsplit(docs[j]["url"]).hostname or ""
            ranked.append((score,j,host_a==host_b))
        for score,j,same_host in sorted(ranked,reverse=True)[:top_per_source]:
            edges[(i,j)]={"a":d["id"],"b":docs[j]["id"],"score":round(score,4),
                "same_host":same_host,"status":"candidate_only_not_event_identity"}
    graph=collections.defaultdict(set)
    for i,j in edges:graph[i].add(j);graph[j].add(i)
    seen=set();contexts=[]
    for i in sorted(graph):
        if i in seen:continue
        stack=[i];seen.add(i);members=[]
        while stack:
            k=stack.pop();members.append(k)
            for v in graph[k]:
                if v not in seen:seen.add(v);stack.append(v)
        contexts.append({"source_ids":[docs[k]["id"] for k in sorted(members)],
            "status":"requires_semantic_event_review"})
    return {"schema_version":1,"method":"metadata_tfidf_blocked_retrieval",
        "summary":{"sources":len(docs),"candidate_pairs":len(edges),"review_contexts":len(contexts),
          "sources_with_candidates":len(graph),"standalone_sources":len(docs)-len(graph)},
        "sources":docs,"candidate_pairs":list(edges.values()),"review_contexts":contexts,
        "limitations":["Similarity is not event identity; no automatic merges.",
         "Missing dates do not block candidates; when both dates exist the day-gap filter applies.",
         "Connected components are review contexts, NOT cards; transitive links may join unrelated events.",
         "No full text required at retrieval stage; semantic adjudication and evidence checks follow.",
         "No automatic topic or nucleus creation or public publication."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--threshold",type=float,default=.42)
    p.add_argument("--top-per-source",type=int,default=8)
    a=p.parse_args();data=json.loads(a.input.read_text())
    rows=data if isinstance(data,list) else data["items"]
    out=retrieve(rows,threshold=a.threshold,top_per_source=a.top_per_source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(out["summary"]))
if __name__=="__main__":main()
