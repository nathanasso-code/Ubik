"""Bounded hybrid social follow-up from GLOBAL discovered terms, never topic names.

Mastodon hashtag timeline and Bluesky full-text search are sampled with the
same observed global candidate term. This is not a social firehose.
"""
import argparse,json
from pathlib import Path
from .topic_social_discovery import collect_bluesky,collect_mastodon
from .transport import get_json

def sample(candidate_report,*,instances=("mastodon.social",),max_terms=6,limit=20,fetch=get_json):
    if not 1<=max_terms<=12 or not 1<=limit<=40 or len(instances)>3:
        raise ValueError("Invalid global social query budget")
    candidates=candidate_report.get("candidate_terms") or []
    terms=[c["term"] for c in candidates if c.get("publisher_hosts",0)>=2
           and isinstance(c.get("term"),str) and c["term"].isalpha()
           and 5<=len(c["term"])<=40][:max_terms]
    records=[];errors=[]
    for term in terms:
        try:records.extend(collect_bluesky(term,limit,fetch))
        except (ValueError,RuntimeError,OSError) as exc:
            errors.append({"provider":"bluesky","term":term,"error_type":type(exc).__name__})
        for instance in instances:
            try:records.extend(collect_mastodon(instance,term,limit,fetch))
            except (ValueError,RuntimeError,OSError) as exc:
                errors.append({"provider":"mastodon","term":term,"instance":instance,
                               "error_type":type(exc).__name__})
    unique={r["id"]:r for r in records}
    documents={}
    for record in unique.values():
        for url in (record.get("metadata") or {}).get("linked_documents",[]):
            d=documents.setdefault(url,{"url":url,"posts":set(),"providers":set()})
            d["posts"].add(record["url"]);d["providers"].add(record["connector"])
    return {"schema_version":1,"purpose":"global_candidate_social_followup",
            "query_origin":"observed_publisher_titles_not_topic_seeds",
            "queries":terms,"observations":list(unique.values()),
            "documents":[{"url":v["url"],"post_urls":sorted(v["posts"]),
                          "providers":sorted(v["providers"])} for v in documents.values()],
            "errors":errors,
            "limitations":["Query expansion uses observed title terms and can drift.",
                           "Bluesky full-text search and one Mastodon hashtag timeline are not exhaustive.",
                           "No independent corroboration or automatic topic routing is implied."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--max-terms",type=int,default=6)
    p.add_argument("--limit",type=int,default=20)
    p.add_argument("--live",action="store_true")
    a=p.parse_args()
    if not a.live:
        print(json.dumps({"dry_run":True,"network_calls":0}));return
    result=sample(json.loads(a.candidates.read_text(encoding="utf-8")),
                  max_terms=a.max_terms,limit=a.limit)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"queries":result["queries"],"posts":len(result["observations"]),
                      "social_document_hints":len(result["documents"]),
                      "errors":result["errors"]},ensure_ascii=False))
if __name__=="__main__":main()
