"""Paired experiment: conservative review vs same review plus cross-card duplicate audit."""
import argparse, json, os, sys
from pathlib import Path
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ingestion.frozen_qwen_passages_two_track import main as base_main, call

AUDIT_PROMPT="""You audit two already-produced information cards for redundant splitting. Default to keeping separate unless the ORIGINAL source-specific news summaries show the same underlying decision/event, or tightly related developments that can be faithfully presented in one inclusive card. Distinguish real facts from merely shared topics. If merge=true, return an accurate inclusive title and summary that represent BOTH cards, preserving meaningful differences; provide a concrete source-grounded reason. Never merge if the resulting card would conflate unrelated events. Return ONLY JSON {"merge":true,"title":"...","summary":"...","reason":"..."} or {"merge":false,"reason":"..."}."""
def audit_context(ctx, model, stats, errors, threshold, max_pairs):
    cards=ctx["cards"]
    if len(cards)<2:
        return dict(ctx, cards_after_audit=cards, audit={"reviewed_pairs":[],"merged_pairs":[],"before":len(cards),"after":len(cards)})
    descriptions=[(c.get("title") or "")+". "+(c.get("summary") or "")+" "+" ".join(x.get("summary","") for x in c.get("source_summaries",[]))[:600] for c in cards]
    sim=cosine_similarity(model.encode(descriptions,normalize_embeddings=True,show_progress_bar=False))
    # Test highly similar card pairs, including those from different embedding components.
    pairs=sorted(((float(sim[i,j]),i,j) for i in range(len(cards)) for j in range(i+1,len(cards)) if sim[i,j]>=threshold),reverse=True)[:max_pairs]
    parent=list(range(len(cards)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    decisions=[]
    for score,i,j in pairs:
        if root(i)==root(j):continue
        a,b=cards[i],cards[j]
        payload={"card_a":{"title":a["title"],"news":[{"id":x["news_id"],"title":x["original_title"],"summary":x["summary"],"evidence":x.get("evidence",[])} for x in a["source_summaries"]]},"card_b":{"title":b["title"],"news":[{"id":x["news_id"],"title":x["original_title"],"summary":x["summary"],"evidence":x.get("evidence",[])} for x in b["source_summaries"]]}}
        try:
            answer=call(AUDIT_PROMPT,payload,stats)
            merge=answer.get("merge") is True and isinstance(answer.get("title"),str) and bool(answer["title"].strip()) and isinstance(answer.get("summary"),str) and bool(answer["summary"].strip()) and bool(answer.get("reason"))
            decisions.append({"card_ids":[a["id"],b["id"]],"similarity":round(score,4),"merge":merge,"reason":answer.get("reason"),"title":answer.get("title") if merge else None,"summary":answer.get("summary") if merge else None})
            if merge:parent[root(j)]=root(i)
        except Exception as exc:errors.append({"phase":"cross_card_audit","context":ctx["context"],"error":str(exc)[:200]})
    components=defaultdict(list)
    for i in range(len(cards)):components[root(i)].append(i)
    merged=[]
    for indexes in components.values():
        members=[cards[i] for i in indexes]
        if len(members)==1:merged.append(members[0]);continue
        ids={c["id"] for c in members}
        supporting=[d for d in decisions if d["merge"] and set(d["card_ids"]).issubset(ids)]
        source_summaries=[x for c in members for x in c["source_summaries"]]
        chosen=supporting[-1] if supporting else {}
        merged.append({"id":"audited-"+members[0]["id"],"title":chosen.get("title") or members[0]["title"],"summary":chosen.get("summary") or members[0]["summary"],"relation":"audited_related","news_ids":[x["news_id"] for x in source_summaries],"source_ids":list(dict.fromkeys(x["source_id"] for x in source_summaries)),"source_summaries":source_summaries,"merged_from":[c["id"] for c in members]})
    assert sorted(x for c in merged for x in c["news_ids"])==sorted(x for c in cards for x in c["news_ids"])
    return dict(ctx,cards_after_audit=merged,audit={"reviewed_pairs":decisions,"merged_pairs":[d for d in decisions if d["merge"]],"before":len(cards),"after":len(merged)})
def main():
    p=argparse.ArgumentParser()
    p.add_argument("grounded");p.add_argument("texts");p.add_argument("--output",required=True);p.add_argument("--max-review",type=int,default=50);p.add_argument("--audit-threshold",type=float,default=.60);p.add_argument("--max-audit-pairs",type=int,default=65)
    a=p.parse_args()
    baseline=Path(a.output).with_name("shared_base.json")
    sys.argv=[sys.argv[0],a.grounded,a.texts,"--output",str(baseline),"--max-review",str(a.max_review)]
    base_main()
    result=json.loads(baseline.read_text())
    result["experiment"]="paired_conservative_review_vs_cross_card_audit"
    result["arms"]={"A":"conservative review without cross-card audit","B":"same frozen cards plus cross-card redundancy audit"}
    model=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
    for variant,record in result["variants"].items():
        record["contexts"]=[audit_context(c,model,result["usage"],result["errors"],a.audit_threshold,a.max_audit_pairs) if c.get("cards") else dict(c,cards_after_audit=c.get("cards",[]),audit={"before":0,"after":0,"reviewed_pairs":[],"merged_pairs":[]}) for c in record["contexts"]]
        record["totals"]["cards_after_audit"]=sum(len(c["cards_after_audit"]) for c in record["contexts"])
        record["totals"]["audit_approved_merges"]=sum(len(c["audit"]["merged_pairs"]) for c in record["contexts"])
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({"variants":{k:v["totals"] for k,v in result["variants"].items()},"errors":len(result["errors"])}))
if __name__=="__main__":main()
