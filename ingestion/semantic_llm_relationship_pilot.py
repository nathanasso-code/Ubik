"""Review-only LLM classification of semantic candidate pairs with substantial original texts.

Never publishes cards or nuclei; preserves URLs and verdicts, not copyrighted bodies.
"""
import argparse,json,os,collections,urllib.error
from pathlib import Path
from ingestion.cross_source_llm_adjudication import acquire,passages,provider_error_code
from ingestion.llm_semantic_adapter import request_analysis

SYSTEM=("Classify the relationship between two independently retrieved source documents. "
"Do not assume they cover the same event merely because embeddings found them similar. "
"Choose exactly one relation: same_news_development (same specific event or news development suitable for ONE multi-source epistemic card), "
"related_separate_developments (distinct developments potentially connected), "
"same_persistent_issue (same scoped long-running question but not the same news development), "
"topic_only (broad topical affinity only), unrelated, insufficient_evidence. "
"An epistemic card summarizes one news item; a persistent nucleus may group several cards, but must not be created automatically. "
"Check what happened, where, when, actors, and temporal sequence. "
"Different emphasis, complementary facts and omitted details do NOT establish separate events. "
"Conversely common actors, region or broad subject do NOT establish one event. "
"Select one existing passage ID from EACH article that best supports the classification. "
"Return JSON keys: relation, reason (brief), evidence_a_id, evidence_b_id, confidence (low,medium,high). "
"Never invent passages or facts; choose insufficient_evidence if original text is inconclusive.")

LABELS={"same_news_development","related_separate_developments","same_persistent_issue","topic_only","unrelated","insufficient_evidence"}

def classify(pairs,limit=60,acquirer=acquire,requester=request_analysis,endpoint="",model="",key=""):
    cache={};results=[];attempted=0
    for pair in pairs:
        if len(results)>=limit:break
        a,b=pair["left"],pair["right"]
        urls=[a["url"],b["url"]]
        for url in urls:
            if url not in cache:
                try:cache[url]={"text":acquirer(url)}
                except (OSError,ValueError,PermissionError,TimeoutError,urllib.error.URLError) as exc:
                    cache[url]={"error":type(exc).__name__}
        if any("text" not in cache[u] for u in urls):continue
        attempted+=1
        pa=passages(cache[urls[0]]["text"][:7000],"A")
        pb=passages(cache[urls[1]]["text"][:7000],"B")
        try:
            proposal,usage=requester([{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps({"a":{"title":a["title"],"passages":pa},
                     "b":{"title":b["title"],"passages":pb}},ensure_ascii=False)}],endpoint,model,key)
            label=proposal.get("relation")
            valid_ids=proposal.get("evidence_a_id") in {p["id"] for p in pa} and proposal.get("evidence_b_id") in {p["id"] for p in pb}
            valid_label=label in LABELS
            results.append({"left":a,"right":b,"embedding_similarity":pair.get("similarity"),
                "status":"analyzed","relation":label if valid_label else "invalid",
                "reason":str(proposal.get("reason",""))[:500],
                "confidence":proposal.get("confidence") if proposal.get("confidence") in ("low","medium","high") else None,
                "evidence_a_id":proposal.get("evidence_a_id") if valid_ids else None,
                "evidence_b_id":proposal.get("evidence_b_id") if valid_ids else None,
                "passage_ids_valid":bool(valid_ids),"accepted_for_review":bool(valid_ids and valid_label),
                "usage":usage})
        except (OSError,ValueError,TypeError,KeyError,TimeoutError,urllib.error.URLError) as exc:
            results.append({"left":a,"right":b,"status":"error","error_type":type(exc).__name__,
                            "http_status":getattr(exc,"code",None),"provider_error_code":provider_error_code(exc)})
    return {"schema_version":1,"model":model,"summary":{
        "semantic_pairs_supplied":len(pairs),"pairs_with_substantial_text_attempted":attempted,
        "analyzed":sum(x["status"]=="analyzed" for x in results),
        "accepted_for_review":sum(x.get("accepted_for_review",False) for x in results),
        "errors":sum(x["status"]=="error" for x in results),
        "labels":dict(collections.Counter(x.get("relation") for x in results if x["status"]=="analyzed")),
        "unique_urls_accessed":len(cache),
        "unique_urls_with_substantial_text":sum("text" in v for v in cache.values())},
        "results":results,"limitations":[
          "Only semantic top-ranked pairs with accessible >=800-character and >=100-word original texts are analyzed.",
          "The output is LLM-proposed, not a human-verified gold standard.",
          "Passage ID validity does not establish evidential relevance.",
          "No cards, nuclei or topic assignments are published.",
          "No article bodies or verbatim excerpts are persisted."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int,default=60);a=p.parse_args()
    endpoint=os.getenv("UBIK_LLM_ENDPOINT","");model=os.getenv("UBIK_LLM_MODEL","");key=os.getenv("UBIK_LLM_API_KEY","")
    if not (endpoint and model and key):p.error("Missing LLM endpoint/model/key")
    source=json.loads(a.input.read_text())
    result=classify(source["candidates"],limit=min(100,max(1,a.limit)),endpoint=endpoint,model=model,key=key)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Semantic LLM relationship adjudication:",json.dumps(result["summary"]))
if __name__=="__main__":main()
