"""Frozen, deliberately limited Ubik benchmark: evaluate retrieved edges and critical cards.

Gold labels are an initial editorial reading of RSS titles/descriptions, NOT a
blind or independent full-text gold standard. Exclude ambiguous olive-incident
within-group pairs. Never treat perfect scores here as production accuracy.
"""
import argparse,itertools,json,zipfile
from pathlib import Path

GROUPS={
"pope_discharge":"S173 S197 S213 S372 S427 S449 S489 S623 S962",
"pope_photos":"S411 S441",
"olive_unresolved":"S220 S306 S392 S483 S603 S958",
"monarch_duplicate":"S473 S474",
"bossware_formats":"S895 S899",
"diplomatic_convoy":"S391 S452"}
def evaluate(candidates,critical):
    labels={sid:label for label,ids in GROUPS.items() for sid in ids.split()}
    sources={s["id"]:s for s in candidates["sources"] if s["id"] in labels}
    edges={tuple(sorted((e["a"],e["b"]))) for e in candidates["candidate_pairs"]}
    final=set()
    for review in critical["reviews"]:
        for card in review.get("cards",[]):
            final.update(tuple(sorted(x)) for x in itertools.combinations(card["source_ids"],2))
    rows=[]
    for a,b in itertools.combinations(sorted(sources),2):
        same=labels[a]==labels[b]
        gold="UNRESOLVED" if same and labels[a]=="olive_unresolved" else ("SAME" if same else "DIFFERENT")
        rows.append({"a":a,"b":b,"gold":gold,"retrieval_direct":(a,b) in edges,"critical_qwen":(a,b) in final})
    valid=[r for r in rows if r["gold"]!="UNRESOLVED"]
    def metrics(field):
        tp=sum(r["gold"]=="SAME" and r[field] for r in valid)
        fp=sum(r["gold"]=="DIFFERENT" and r[field] for r in valid)
        fn=sum(r["gold"]=="SAME" and not r[field] for r in valid)
        tn=sum(r["gold"]=="DIFFERENT" and not r[field] for r in valid)
        return {"tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":tp/(tp+fp) if tp+fp else None,
            "recall":tp/(tp+fn) if tp+fn else None}
    return {"summary":{"sources":len(sources),"pairs":len(rows),"scored_pairs":len(valid),
        "unresolved_pairs":len(rows)-len(valid),"retrieval_direct":metrics("retrieval_direct"),
        "critical_qwen":metrics("critical_qwen")},
        "labels":labels,"sources":list(sources.values()),"pairs":rows,
        "limitations":["Selection bias: the 23 sources were selected from Qwen proposals.",
          "Initial labels were formed by editorial reading of the same metadata Qwen saw; evaluation is NOT independent.",
          "Olive-harvest within-case comparisons are unresolved until full-text reading.",
          "Not a head-to-head comparison with the old 43-source full-text experiment.",
          "Scores cannot establish population precision or recall."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("--candidates",type=Path,required=True)
    p.add_argument("--critical",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();result=evaluate(json.loads(a.candidates.read_text()),json.loads(a.critical.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result["summary"],ensure_ascii=False))
if __name__=="__main__":main()
