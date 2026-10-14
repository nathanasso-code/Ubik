"""Audit the existing corpus before claiming full-text semantic coverage."""
import argparse,json
from pathlib import Path

TIERS={"substantial_article_text_accessible","long_abstract_metadata"}
def audit(corpus,public,papers):
    docs=corpus.get("documents",[])
    qualified=[d for d in docs if any(t.get("content_tier") in TIERS for t in d.get("access_tests",[]))]
    pages=public.get("documents",[])
    return {"corpus_documents":len(docs),
      "unique_documents_with_rich_access_signal":len(qualified),
      "rich_access_candidates":[{"url":d["url"],"title":(d.get("titles") or [""])[0],
          "description":(d.get("descriptions") or [""])[0],
          "tier":next((t.get("content_tier") for t in d.get("access_tests",[]) if t.get("content_tier") in TIERS),"unknown")}
          for d in qualified],
      "public_pages_probed":len(pages),
      "pages_with_2000_plus_extracted_chars":sum(p.get("text_chars",0)>=2000 for p in pages),
      "pages_with_full_text_persisted":sum(p.get("full_text_persisted") is True for p in pages),
      "licensed_papers_available":len(papers.get("documents",[])),
      "limitations":["Access signal does not imply stored full text.","Only stored bodies may be used for full-text analysis.",
          "Candidate count is not a validated cluster of related news."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corpus",type=Path,required=True)
    p.add_argument("--public",type=Path,required=True)
    p.add_argument("--rich",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(json.loads(a.corpus.read_text()),json.loads(a.public.read_text()),json.loads(a.rich.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="rich_access_candidates" and k!="limitations"}))
if __name__=="__main__":main()
