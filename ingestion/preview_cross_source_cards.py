"""Preview source-connected candidate cards, not verified event clusters."""
import argparse,collections,json
from pathlib import Path

def build(data):
    parent={};sources={}
    def root(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=root(parent[x])
        return parent[x]
    def union(a,b):
        ra,rb=root(a),root(b)
        if ra!=rb:parent[rb]=ra
    edges=[]
    for p in data["pairs"]:
        if not p.get("both_800_100"):continue
        a,b=p["left"],p["right"]
        for s in (a,b):sources[s["url"]]={"url":s["url"],"title":s["title"],"publisher":s["publisher"]}
        union(a["url"],b["url"])
        edges.append({"a":a["url"],"b":b["url"],"rss_similarity":p["score"]})
    groups=collections.defaultdict(list)
    for url,s in sources.items():groups[root(url)].append(s)
    cards=[]
    for members in groups.values():
        urls={s["url"] for s in members}
        card_edges=[e for e in edges if e["a"] in urls and e["b"] in urls]
        cards.append({"status":"candidate_graph_component_unverified",
                      "sources":sorted(members,key=lambda x:x["publisher"]),
                      "edges":card_edges,
                      "warning":"Connected paths do not prove all sources describe the same event."})
    cards.sort(key=lambda x:-len(x["sources"]))
    return {"schema_version":1,"cards":cards,
            "summary":{"source_connected_components":len(cards),"unique_sources":len(sources),
                       "supported_edges":len(edges)},
            "limitations":["These are graph components of metadata-selected, text-accessible pairs; not verified semantic clusters.",
                           "No extracted article bodies are compared or stored."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();r=build(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("Candidate card preview:",json.dumps(r["summary"]))
if __name__=="__main__":main()
