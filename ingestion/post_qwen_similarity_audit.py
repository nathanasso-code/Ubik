"""Post-Qwen TF-IDF and multilingual embedding diagnostic; never auto-merge."""
import argparse,json
from pathlib import Path

def audit(review,model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sentence_transformers import SentenceTransformer
    import numpy as np
    cases=[];model=SentenceTransformer(model_name)
    for case in review["reviews"]:
        facts=case["source_facts"]
        ids=[f["source_id"] for f in facts]
        texts=[" ".join(str(f.get(k) or "") for k in ("subject","action","object","central_development","result_or_consequence")) for f in facts]
        if len(ids)<2:continue
        if not any(t.strip() for t in texts):continue
        lex=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,token_pattern=r"(?u)\b\w+\b").fit_transform(texts)
        tf=(lex@lex.T).toarray()
        vectors=model.encode(texts,normalize_embeddings=True,show_progress_bar=False)
        sem=np.asarray(vectors)@np.asarray(vectors).T
        merged={tuple(sorted((a,b))) for card in case["cards"] for i,a in enumerate(card["source_ids"]) for b in card["source_ids"][i+1:]}
        pairs=[]
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                a,b=ids[i],ids[j]
                eligible=all(facts[k].get("information_quality")=="substantive" for k in (i,j))
                t,s=float(tf[i,j]),float(sem[i,j])
                pairs.append({"a":a,"b":b,"tfidf":round(t,4),"embedding":round(s,4),
                  "qwen_same_card":tuple(sorted((a,b))) in merged,
                  "both_substantive":eligible,
                  "diagnostic":"high_similarity_different_cards" if eligible and t>=.48 and s>=.78 and tuple(sorted((a,b))) not in merged else
                  "low_similarity_same_card" if (t<.18 or s<.58) and tuple(sorted((a,b))) in merged else "review_only"})
        cases.append({"source_ids":ids,"pairs":pairs})
    return {"method":"post_qwen_tfidf_plus_multilingual_embedding_diagnostic",
      "cases":cases,"note":"Scores are diagnostic, not identity decisions; thresholds exploratory, not calibrated."}

def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();result=audit(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print("POST_QWEN_AUDIT",json.dumps({"cases":len(result["cases"]),"flagged_pairs":sum(p["diagnostic"]!="review_only" for c in result["cases"] for p in c["pairs"])}))
if __name__=="__main__":main()
