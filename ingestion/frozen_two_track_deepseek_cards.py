"""Two controlled embedding representations followed by bounded DeepSeek identity adjudication."""
import argparse, json, os, re, time
from pathlib import Path
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ingestion.llm_semantic_adapter import request_analysis

TITLE_PROMPT="""Produce a SHORT, SPECIFIC additional event-identity headline for EACH supplied news item. Keep the concrete actor, action, object and essential qualifier; do not introduce information. Return JSON {"titles":[{"id":"...","title":"..."}]}. Preserve every ID."""
REVIEW_PROMPT="""Determine whether the supplied news items refer to the SAME SPECIFIC event/development, rather than merely sharing a topic, person or broad story. Consider source-grounded news summaries and evidence. Group only strictly equivalent developments; preserve all input IDs exactly once, including singletons. Related reactions or distinct decisions must remain separate. Return JSON {"groups":[{"ids":["..."],"reason":"short factual reason"}]}. No new facts. Do not omit or duplicate IDs."""

def call(prompt,payload,stats):
    result,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
    stats["calls"]+=1
    if not isinstance(result,dict):raise ValueError("Invalid JSON response")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("grounded",type=Path);p.add_argument("texts",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--threshold",type=float,default=.68);p.add_argument("--max-review",type=int,default=50)
    a=p.parse_args()
    base=json.loads(a.grounded.read_text())
    corpus=json.loads(a.texts.read_text())
    bodies={x["source_id"]:x.get("text","")[:7000] for x in corpus["sources"] if x.get("text")}
    model=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
    output={"experiment":"title_augmented_summary_vs_original_text_embedding_deepseek","threshold":a.threshold,"max_review_per_variant":a.max_review,"variants":{},"titles":{},"usage":{"calls":0},"errors":[]}
    all_items=[n for ctx in base["contexts"] for n in ctx["news"]]
    # Context-qualified IDs prevent collisions of n0 across contexts.
    for ctx in base["contexts"]:
        news=ctx["news"]
        if not news:continue
        payload=[{"id":n["id"],"title":n["title"],"summary":n["summary"]} for n in news]
        try:
            r=call(TITLE_PROMPT,{"news":payload},output["usage"])
            proposed={x["id"]:x["title"] for x in r.get("titles",[]) if isinstance(x,dict) and isinstance(x.get("title"),str)}
        except Exception as exc:
            output["errors"].append({"context":ctx["context"],"phase":"titles","error":str(exc)[:200]});proposed={}
        for n in news:
            output["titles"][str(ctx["context"])+":"+n["id"]]=proposed.get(n["id"],n["title"])
    for variant in ("summary","source_text"):
        contexts=[];review_count=0
        for ctx in base["contexts"]:
            items=ctx["news"];n=len(items)
            if not n:
                contexts.append({"context":ctx["context"],"cards":[],"reviewed_pairs":[]});continue
            title=lambda x:output["titles"][str(ctx["context"])+":"+x["id"]]
            if variant=="summary":
                passages=[title(x)+". "+x["title"]+". "+x["summary"] for x in items]
            else:
                # Full original text, with the news-specific title anchoring the target development.
                # For multiple news from one source, the body repeats; this is a controlled limitation.
                passages=[title(x)+". "+x["title"]+". "+bodies.get(x["source_id"],x["summary"]) for x in items]
            vectors=model.encode(passages,normalize_embeddings=True,show_progress_bar=False)
            sim=cosine_similarity(vectors)
            # Build candidate graph by cosine similarity, then review connected components.
            parent=list(range(n))
            def find(i):
                while parent[i]!=i:
                    parent[i]=parent[parent[i]];i=parent[i]
                return i
            def union(i,j):
                a0,b0=find(i),find(j)
                if a0!=b0:parent[b0]=a0
            candidates=sorted(((float(sim[i,j]),i,j) for i in range(n) for j in range(i+1,n) if items[i]["source_id"]!=items[j]["source_id"] and sim[i,j]>=a.threshold),reverse=True)
            for _,i,j in candidates:union(i,j)
            components=defaultdict(list)
            for i in range(n):components[find(i)].append(i)
            groups=[];reviewed=[]
            for comp in components.values():
                if len(comp)==1:
                    groups.append([comp[0]]);continue
                # Keep review bounded; never automatically merge unreviewed components.
                if review_count>=a.max_review:
                    groups.extend([[i] for i in comp]);continue
                # Large connected components split into batches; do not merge across batches without review.
                for start in range(0,len(comp),15):
                    sub=comp[start:start+15]
                    if len(sub)==1:groups.append(sub);continue
                    review_count+=1
                    payload=[{"id":items[i]["id"],"title":title(items[i]),"summary":items[i]["summary"],"source_id":items[i]["source_id"]} for i in sub]
                    try:
                        response=call(REVIEW_PROMPT,{"news":payload},output["usage"])
                        remaining={items[i]["id"]:i for i in sub}
                        for g in response.get("groups",[]):
                            ids=g.get("ids",[])
                            if not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)) or any(k not in remaining for k in ids):continue
                            groups.append([remaining.pop(k) for k in ids])
                        groups.extend([[i] for i in remaining.values()])
                        reviewed.append({"ids":[items[i]["id"] for i in sub],"status":"reviewed"})
                    except Exception as exc:
                        groups.extend([[i] for i in sub])
                        output["errors"].append({"variant":variant,"context":ctx["context"],"error":str(exc)[:200]})
            # Preserve all source-specific news and verified evidence.
            source_evidence={}
            for card in ctx["cards"]:
                for e in card.get("evidence",[]):source_evidence[e["news_id"]]=e.get("passages",[])
            cards=[]
            for k,group in enumerate(groups):
                members=[items[i] for i in group]
                cards.append({"id":f"{variant}-{ctx['context']}-{k}","title":title(members[0]),"news_ids":[m["id"] for m in members],"source_ids":list(dict.fromkeys(m["source_id"] for m in members)),"source_summaries":[{"news_id":m["id"],"source_id":m["source_id"],"original_title":m["title"],"additional_title":title(m),"summary":m["summary"],"evidence":source_evidence.get(m["id"],[])} for m in members]})
            assert sorted(k for c in cards for k in c["news_ids"])==sorted(x["id"] for x in items)
            contexts.append({"context":ctx["context"],"news":n,"cards":cards,"candidate_pairs":len(candidates),"reviewed_components":len(reviewed)})
        output["variants"][variant]={"contexts":contexts,"totals":{"news":sum(c.get("news",0) for c in contexts),"cards":sum(len(c["cards"]) for c in contexts),"reviewed_components":review_count}}
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2))
    print(json.dumps({"variants":{k:v["totals"] for k,v in output["variants"].items()},"usage":output["usage"],"errors":len(output["errors"])}))
if __name__=="__main__":main()
