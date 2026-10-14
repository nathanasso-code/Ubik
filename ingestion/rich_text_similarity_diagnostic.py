"""Diagnostic title-versus-body TF-IDF experiment on already stored licensed texts.

No model API; no claim of event identity or semantic accuracy.
"""
import argparse,json,re,math,collections,itertools,statistics
from pathlib import Path
STOP=set("the and for with from this that have into after over about said says will were their a an of to in on at as by is are was be it its new not study research results methods introduction discussion conclusion patients using use used data".split())
def vector(text):
    terms=[x for x in re.findall(r"[a-z]{3,}",text.lower()) if x not in STOP]
    return collections.Counter(terms)
def similarity(a,b):
    if not a or not b:return 0.
    return sum(v*b.get(k,0) for k,v in a.items())/math.sqrt(sum(v*v for v in a.values())*sum(v*v for v in b.values()))
def experiment(papers):
    docs=papers.get("documents",[])
    rows=[]
    for a,b in itertools.combinations(docs,2):
        rows.append({"url_a":a["url"],"url_b":b["url"],
          "title_similarity":round(similarity(vector(a["title"]),vector(b["title"])),4),
          "body_similarity":round(similarity(vector(a["text"]),vector(b["text"])),4)})
    return {"documents":len(docs),"pairs":len(rows),
      "median_title_similarity":round(statistics.median(x["title_similarity"] for x in rows),4) if rows else None,
      "median_body_similarity":round(statistics.median(x["body_similarity"] for x in rows),4) if rows else None,
      "top_body_pairs":sorted(rows,key=lambda x:-x["body_similarity"])[:10],
      "limitations":["Unweighted bag-of-words cosine, not E5/NLI or semantic accuracy.",
        "Common scientific vocabulary inflates full-body similarity; use chunk retrieval and independent labels.",
        "Nine unrelated papers cannot evaluate same-event news grouping."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("--rich",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();out=experiment(json.loads(a.rich.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="top_body_pairs" and k!="limitations"}))
if __name__=="__main__":main()
