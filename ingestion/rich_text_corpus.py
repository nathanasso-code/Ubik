"""Build a reproducible rich-text corpus from explicitly retained licensed papers.

Avoids using title/description-only inputs and preserves provenance.
"""
import argparse,json,re
from pathlib import Path

def build(directory,minimum_chars=2000,max_chars=30000):
    documents=[];rejected=[]
    for path in sorted(Path(directory).glob("*.json")):
        try:
            item=json.loads(path.read_text(encoding="utf-8"))
            body=item.get("text","")
            if not isinstance(body,str) or len(body.strip())<minimum_chars:
                rejected.append({"file":path.name,"reason":"insufficient_text"});continue
            if not item.get("license_evidence") or not item.get("url"):
                rejected.append({"file":path.name,"reason":"missing_license_or_url"});continue
            # Truncation is explicit and counted, never silently presented as full text.
            documents.append({"url":item["url"],"source_id":"europepmc","title":item.get("title",""),
                "text":body[:max_chars],"original_text_chars":len(body),
                "text_truncated":len(body)>max_chars,"license_evidence":item["license_evidence"],
                "text_quality":"licensed_substantial_body","source_file":path.name})
        except (OSError,ValueError,TypeError):
            rejected.append({"file":path.name,"reason":"unreadable"})
    return {"schema_version":1,"documents":documents,"rejected":rejected,
        "coverage":{"rich_documents":len(documents),"rejected":len(rejected),
            "original_text_characters":sum(x["original_text_chars"] for x in documents)},
        "limitations":["Scientific articles form a domain-specific sample, not a representative global news benchmark.",
          "Licensed text availability does not establish semantic quality or topical clustering.",
          "Source license and attribution require review before public redistribution."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("--texts",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--minimum-chars",type=int,default=2000)
    a=p.parse_args();result=build(a.texts,a.minimum_chars)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result["coverage"]))
if __name__=="__main__":main()
