"""Consolidate overlapping provisional Qwen proposals into disjoint REVIEW CASES.

This is NOT card merging: it produces one critical-review case per overlap
component, preserves every proposal and its source provenance, and identifies
contested memberships. Requires explicit split/confirmation downstream.
"""
import argparse,collections,json
from pathlib import Path

def consolidate(data):
    proposals=data.get("candidate_groups",[])
    docs={s["id"]:s for s in data.get("sources",[])}
    parent=list(range(len(proposals)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def union(a,b):
        ra,rb=root(a),root(b)
        if ra!=rb:parent[rb]=ra
    memberships=collections.defaultdict(list)
    for i,p in enumerate(proposals):
        for sid in set(p.get("source_ids",[])):
            memberships[sid].append(i)
    for ids in memberships.values():
        for i in ids[1:]:union(ids[0],i)
    components=collections.defaultdict(list)
    for i in range(len(proposals)):components[root(i)].append(i)
    cases=[]
    for indices in components.values():
        counts=collections.Counter(sid for i in indices for sid in set(proposals[i]["source_ids"]))
        ids=sorted(counts)
        variants=[{"source_ids":proposals[i]["source_ids"],"reason":proposals[i].get("reason","")} for i in indices]
        cases.append({"case_id":f"C{len(cases)+1}","source_ids":ids,
          "source_count":len(ids),"proposal_count":len(indices),
          "proposal_variants":variants,
          "contested_source_ids":[sid for sid in ids if counts[sid]<len(indices)],
          "sources":[docs[sid] for sid in ids if sid in docs],
          "status":"requires_explicit_critical_split_review"})
    cases.sort(key=lambda x:(-x["proposal_count"],-x["source_count"],x["case_id"]))
    for i,c in enumerate(cases):c["case_id"]=f"C{i+1}"
    return {"schema_version":1,"summary":{"input_proposals":len(proposals),
       "review_cases":len(cases),"cases_with_conflicting_membership":sum(bool(c["contested_source_ids"]) for c in cases),
       "sources_in_review_cases":len(memberships),"unreviewed_windows":data.get("summary",{}).get("unreviewed_windows")},
       "cases":cases,"limitations":["Cases are not cards; overlapping proposals never trigger automatic merge.",
        "Membership frequency measures proposal disagreement, not event probability.",
        "Only already-reviewed Qwen proposals are included; unretrieved events remain unknown."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();result=consolidate(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result["summary"]))
    for c in result["cases"]:print("REVIEW_CASE",c["case_id"],c["source_count"],c["proposal_count"],c["contested_source_ids"])
if __name__=="__main__":main()
