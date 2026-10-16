"""Reproducible cross-publisher candidate mining; NOT verified event clustering.

Uses RSS title + bounded description only. Does not call LLMs or store article bodies.
"""
import argparse,collections,json,math,re
from pathlib import Path
from urllib.parse import urlsplit

STOP=set("the a an of to in for on at from with by and or as is are was were be this that its it after over into about amid says said new how why what who will can may has have had their his her more than".split())
def tokens(s):
    return [x for x in re.findall(r"[a-z0-9]+",str(s).lower()) if len(x)>2 and x not in STOP]
def build(rows):
    unique={}
    for row in rows:
        url=row.get("url","")
        if not url or url in unique:continue
        title=row.get("title","")
        desc=row.get("description","")
        if not title:continue
        unique[url]={"url":url,"publisher":row.get("publisher"),"title":title,
                     "description":str(desc or "")[:500],"host":urlsplit(url).hostname}
    docs=list(unique.values())
    df=collections.Counter()
    counts=[]
    for d in docs:
        # Title is emphasized but short snippets can distinguish closely related stories.
        terms=tokens(d["title"])*2+tokens(d["description"])
        count=collections.Counter(terms)
        counts.append(count)
        df.update(count)
    n=len(docs)
    vectors=[]
    inverted=collections.defaultdict(list)
    for i,count in enumerate(counts):
        vec={t:(1+math.log(c))*math.log(1+(n+1)/(df[t]+1)) for t,c in count.items()}
        norm=math.sqrt(sum(v*v for v in vec.values())) or 1
        vec={t:v/norm for t,v in vec.items()}
        vectors.append(vec)
        for t,v in vec.items():inverted[t].append((i,v))
    scores=collections.defaultdict(float)
    for postings in inverted.values():
        # Skip excessively generic tokens to bound cross-products.
        if len(postings)>200:continue
        for a,(i,vi) in enumerate(postings):
            for j,vj in postings[a+1:]:
                if docs[i]["host"]==docs[j]["host"]:continue
                scores[(i,j)]+=vi*vj
    ranked=sorted(scores.items(),key=lambda z:-z[1])
    pairs=[]
    for (i,j),score in ranked[:100]:
        left,right=docs[i],docs[j]
        lt=set(tokens(left["title"]));rt=set(tokens(right["title"]))
        overlap=sorted(lt&rt)
        pairs.append({"score":round(score,4),"title_overlap":overlap,
                      "same_story":"unreviewed","left":{"title":left["title"],"url":left["url"],"publisher":left["publisher"]},
                      "right":{"title":right["title"],"url":right["url"],"publisher":right["publisher"]}})
    return {"schema_version":1,"method":"sparse_tfidf_rss_title_description","documents":n,
            "cross_publisher_pairs_scored":len(scores),
            "top_pairs":pairs,
            "limitations":["RSS metadata only; not extracted full text or semantic embeddings.",
                           "Similarity is not evidence of same event, redundancy, or contradiction.",
                           "Human adjudication required; top-100 selection is biased toward lexical overlap."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    source=json.loads(a.input.read_text())
    result=build(source["items"])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Cross-publisher candidate mining:",json.dumps({"documents":result["documents"],"pairs_scored":result["cross_publisher_pairs_scored"],"top_pairs":result["top_pairs"][:12]},ensure_ascii=False))
if __name__=="__main__":main()
