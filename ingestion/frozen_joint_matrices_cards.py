"""Joint matrix and factual-card review on the same frozen DeepSeek summaries."""
import argparse,json,os
from pathlib import Path
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ingestion.frozen_independent_qwen_deepseek import ask

PROMPT="""You receive source-grounded factual news summaries and their original source_id. Produce BOTH coherent specific information matrices and distinct factual cards IN THE SAME REVIEW. A matrix is a coherent, specific event, study, decision, or closely connected information context; not merely a broad topic. A matrix may contain multiple substantively different cards. Merge equivalent news summaries into a card; preserve distinct substantial facts as different cards within the same matrix where appropriate. A shared original source is evidence of relationship but not proof of matrix identity; unrelated topics in a long article may need separate matrices. If the input covers unrelated contexts, create multiple matrices. Each input news id must appear in exactly one card and each card in exactly one matrix. Do not invent evidence. Return ONLY JSON {"matrices":[{"title":"...","reason":"...","cards":[{"ids":["..."],"title":"...","summary":"...","reason":"..."}]}]}."""
def components(news,vectors,threshold):
    sim=cosine_similarity(vectors);parent=list(range(len(news)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(i,j):
        x,y=find(i),find(j)
        if x!=y:parent[y]=x
    # Existing cross-source semantic relationships, plus direct same-source
    # provenance, but avoid a huge connected-component chain through generic articles.
    for i in range(len(news)):
        for j in range(i+1,len(news)):
            if sim[i,j]>=threshold or (news[i]["source_id"]==news[j]["source_id"] and sim[i,j]>=0.35):
                union(i,j)
    groups=defaultdict(list)
    for i in range(len(news)):groups[find(i)].append(i)
    return list(groups.values())
def main():
    p=argparse.ArgumentParser()
    p.add_argument("prior_results",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--threshold",type=float,default=.68);p.add_argument("--max-group",type=int,default=28)
    a=p.parse_args()
    prior=json.loads(a.prior_results.read_text());baseline=prior["arms"]["B_deepseek"]
    encoder=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
    out={"experiment":"joint_matrices_and_cards_shared_deepseek_extraction","threshold":a.threshold,
         "max_group":a.max_group,"prompt":PROMPT,"arms":{},"candidate_groups":[]}
    prepared=[]
    for ctx in baseline["contexts"]:
        news_by_id={s["news_id"]:s for card in ctx["cards"] for s in card["sources"]}
        news=[{"id":nid,"title":s["original_title"],"summary":s["summary"],
               "source_id":s["source_id"]} for nid,s in news_by_id.items()]
        vectors=encoder.encode([n["title"]+". "+n["summary"] for n in news],normalize_embeddings=True)
        groups=components(news,vectors,a.threshold)
        # A hard size guard: oversize connected components must not be sent to LLM.
        # Split deterministically into non-overlapping, locally coherent complete-link
        # batches; these are review windows, not validated matrix boundaries.
        review_groups=[]
        for group in groups:
            if len(group)<=a.max_group:review_groups.append(group);continue
            pending=sorted(group,key=lambda i:(news[i]["source_id"],news[i]["id"]))
            sim=cosine_similarity(vectors)
            while pending:
                seed=pending.pop(0);batch=[seed]
                for i in pending[:]:
                    if len(batch)>=a.max_group:break
                    if all(sim[i,j]>=0.50 for j in batch):
                        batch.append(i);pending.remove(i)
                review_groups.append(batch)
        prepared.append((ctx,news,news_by_id,review_groups))
        out["candidate_groups"].append({"context":ctx["context"],"sizes":[len(g) for g in review_groups],
                                         "oversize_split":sum(len(g)>a.max_group for g in groups)})
    for arm,model in [("A_qwen",os.environ["UBIK_QWEN_MODEL"]),("B_deepseek",os.environ["UBIK_LLM_MODEL"])]:
        result={"model":model,"contexts":[],"errors":[],"usage":{"calls":0}}
        for ctx,news,original,groups in prepared:
            matrices=[]
            for k,group in enumerate(groups):
                payload=[news[i] for i in group];expected={x["id"] for x in payload}
                try:
                    if len(group)==1:
                        n=payload[0];response={"matrices":[{"title":n["title"],"reason":"singleton","cards":[{"ids":[n["id"]],"title":n["title"],"summary":n["summary"],"reason":"singleton"}]}]}
                    else:response=ask(model,PROMPT,{"news":payload},result["usage"])
                    raw=response["matrices"]
                    ids=[nid for m in raw for card in m["cards"] for nid in card["ids"]]
                    if len(ids)!=len(expected) or set(ids)!=expected or len(ids)!=len(set(ids)):
                        raise ValueError("Incomplete or duplicated news partition")
                except Exception as e:
                    result["errors"].append({"context":ctx["context"],"group":k,"error":str(e)[:300]})
                    raw=[{"title":n["title"],"reason":"review_failed","cards":[{"ids":[n["id"]],"title":n["title"],"summary":n["summary"],"reason":"review_failed"}]} for n in payload]
                for m in raw:
                    cards=[]
                    for card in m["cards"]:
                        cards.append({"title":card.get("title"),"summary":card.get("summary"),
                                      "reason":card.get("reason"),"news_ids":card["ids"],
                                      "sources":[original[nid] for nid in card["ids"]]})
                    matrices.append({"id":f"{arm}-{ctx['context']}-{len(matrices)}",
                                     "title":m.get("title"),"reason":m.get("reason"),
                                     "review_group":k,"cards":cards,
                                     "source_ids":sorted({s["source_id"] for c in cards for s in c["sources"]})})
            result["contexts"].append({"context":ctx["context"],"matrices":matrices,"input_count":len(news)})
        result["totals"]={"matrices":sum(len(c["matrices"]) for c in result["contexts"]),
                          "cards":sum(sum(len(m["cards"]) for m in c["matrices"]) for c in result["contexts"]),
                          "calls":result["usage"]["calls"],"errors":len(result["errors"])}
        out["arms"][arm]=result
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({k:v["totals"] for k,v in out["arms"].items()}))
if __name__=="__main__":main()
