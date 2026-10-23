"""Compare summary vs DeepSeek-selected verbatim passages; preserve embedding/LLM adjudication audit."""
import argparse, json, os, re, time
from pathlib import Path
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ingestion.llm_semantic_adapter import request_analysis

TITLE_PROMPT="""Produce a SHORT, SPECIFIC additional event-identity headline for EACH supplied news item. Keep the concrete actor, action, object and essential qualifier; do not introduce information. Return JSON {"titles":[{"id":"...","title":"..."}]}. Preserve every ID."""
PASSAGE_PROMPT="""For EACH supplied news item identify 1-3 exact contiguous verbatim excerpts from article_body that directly document the specific claim. Return JSON {"items":[{"id":"...","quotes":["exact substring"]}]}. Do not invent excerpts."""
REVIEW_PROMPT="""Classify as SAME FACT, RELATED DEVELOPMENTS THAT CAN SHARE A CARD, or DISTINCT. Prefer avoiding duplicate cards for the same underlying development. Group same facts or closely related developments that can be accurately represented together. For each group supply relation, inclusive title, concise summary, and reason. Return JSON {"groups":[{"ids":["..."],"relation":"same_fact","title":"...","summary":"...","reason":"..."}]}. Preserve every input ID exactly once. Determine whether the supplied news items refer to the SAME SPECIFIC event/development, rather than merely sharing a topic, person or broad story. Consider source-grounded news summaries and evidence. Group only strictly equivalent developments; preserve all input IDs exactly once, including singletons. Related reactions or distinct decisions must remain separate. Return JSON {"groups":[{"ids":["..."],"reason":"short factual reason"}]}. No new facts. Do not omit or duplicate IDs."""

def call(prompt,payload,stats,model_override=None):
    result,usage=request_analysis([{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],os.environ["UBIK_LLM_ENDPOINT"],model_override or os.environ["UBIK_LLM_MODEL"],os.environ["UBIK_LLM_API_KEY"],timeout=180)
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
    output={"experiment":"deepseek_passage_evidence_vs_summary_embedding","threshold":a.threshold,"max_review_per_variant":a.max_review,"variants":{},"titles":{},"usage":{"calls":0},"errors":[]}
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
    output["deepseek_passages"]={}
    for ctx in base["contexts"]:
        by_source=defaultdict(list)
        for item in ctx["news"]:by_source[item["source_id"]].append(item)
        for sid,news in by_source.items():
            body=bodies.get(sid,"")
            if not body:continue
            try:
                response=call(PASSAGE_PROMPT,{"article_body":body,"news":[{"id":x["id"],"title":x["title"],"summary":x["summary"]} for x in news]},output["usage"],os.environ["UBIK_LLM_MODEL"])
                quotes={x["id"]:x.get("quotes",[]) for x in response.get("items",[]) if isinstance(x,dict)}
            except Exception as exc:
                output["errors"].append({"phase":"deepseek","source_id":sid,"error":str(exc)[:200]});quotes={}
            for item in news:
                verified=[]
                for q in quotes.get(item["id"],[]):
                    if not isinstance(q,str) or not q:continue
                    pos=body.find(q)
                    if pos>=0:verified.append({"text":q,"start":pos,"end":pos+len(q)})
                output["deepseek_passages"][str(ctx["context"])+":"+item["id"]]={"source_id":sid,"passages":verified,"status":"verified" if verified else "missing"}
    for variant in ("summary","selected_passages"):
        contexts=[];review_count=0
        for ctx in base["contexts"]:
            items=ctx["news"];n=len(items)
            if not n:
                contexts.append({"context":ctx["context"],"cards":[],"reviewed_pairs":[]});continue
            title=lambda x:output["titles"][str(ctx["context"])+":"+x["id"]]
            if variant=="summary":
                passages=[title(x)+". "+x["title"]+". "+x["summary"] for x in items]
            else:
                passages=[title(x)+". "+x["title"]+". "+(" ".join(p["text"] for p in output["deepseek_passages"].get(str(ctx["context"])+":"+x["id"],{}).get("passages",[])) or x["summary"]) for x in items]
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
            baseline_components=[{"ids":[items[i]["id"] for i in comp]} for comp in components.values()]
            groups=[];reviewed=[];decisions=[]
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
                            decisions.append({"ids":ids,"relation":g.get("relation"),"title":g.get("title"),"summary":g.get("summary"),"reason":g.get("reason")})
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
                decision=next((d for d in decisions if set(d["ids"])==set(m["id"] for m in members)),None)
                cards.append({"id":f"{variant}-{ctx['context']}-{k}","title":(decision or {}).get("title") or title(members[0]),"summary":(decision or {}).get("summary") or (members[0]["summary"] if len(members)==1 else ""),"relation":(decision or {}).get("relation"),"news_ids":[m["id"] for m in members],"source_ids":list(dict.fromkeys(m["source_id"] for m in members)),"source_summaries":[{"news_id":m["id"],"source_id":m["source_id"],"original_title":m["title"],"additional_title":title(m),"summary":m["summary"],"evidence":source_evidence.get(m["id"],[]),"deepseek_evidence":output["deepseek_passages"].get(str(ctx["context"])+":"+m["id"],{})} for m in members]})
            assert sorted(k for c in cards for k in c["news_ids"])==sorted(x["id"] for x in items)
            contexts.append({"context":ctx["context"],"news":n,"cards":cards,"candidate_pairs":len(candidates),"reviewed_components":len(reviewed),"embedding_baseline":{"cards":len(baseline_components),"components":baseline_components},"deepseek_decisions":decisions,"reviewed_batches":reviewed,"comparison":{"embedding_cards":len(baseline_components),"deepseek_cards":len(cards),"delta":len(cards)-len(baseline_components),"split_components":sum(1 for component in baseline_components if sum(bool(set(component["ids"]) & set(card["news_ids"])) for card in cards)>1)}})
        output["variants"][variant]={"contexts":contexts,"totals":{"news":sum(c.get("news",0) for c in contexts),"cards":sum(len(c["cards"]) for c in contexts),"reviewed_components":review_count,"embedding_cards":sum(c.get("embedding_baseline",{}).get("cards",0) for c in contexts),"candidate_pairs":sum(c.get("candidate_pairs",0) for c in contexts)}}
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2))
    print(json.dumps({"variants":{k:v["totals"] for k,v in output["variants"].items()},"usage":output["usage"],"errors":len(output["errors"])}))
if __name__=="__main__":main()
