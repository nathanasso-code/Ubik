"""Topic-agnostic global discovery: document hints and candidate emerging terms.

Consumes existing federated acquisition snapshots. It does NOT fetch new data,
choose a topic, infer event identity, or claim editorial importance.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from .federate import federate

STOP=set("""the and with from this that have were been into about after over under
news live update updates latest breaking world today says said report reports
della delle degli nella sulla sono anche come dopo alla negli delle
russia ukraine russian ukrainian""".split())

def terms(text):
    return {t for t in re.findall(r"[^\W_]+",str(text).casefold(),re.UNICODE)
            if len(t)>=5 and t not in STOP and not t.isdecimal()}

def global_candidates(manifest,*,min_sources=2,max_terms=60):
    if not 2<=min_sources<=20 or not 1<=max_terms<=500:
        raise ValueError("Invalid candidate budget")
    observations=manifest.get("observations") or []
    documents=defaultdict(list)
    for item in observations:
        hint=item.get("canonical_url_hint")
        if isinstance(hint,str) and urlsplit(hint).scheme in ("http","https"):
            documents[hint].append(item)
    # Only distinct documents count for candidate emergence; repeated posts of
    # one URL cannot inflate the term count.
    groups=defaultdict(lambda:{"documents":set(),"sources":set(),"hosts":set()})
    for url,items in documents.items():
        titles=[x.get("title","") for x in items]
        title_terms=set().union(*(terms(x) for x in titles))
        hosts={urlsplit(url).hostname or ""}
        source_ids={(x.get("connector"),x.get("source_id")) for x in items}
        for term in title_terms:
            row=groups[term]
            row["documents"].add(url)
            row["sources"].update(source_ids)
            row["hosts"].update(hosts)
    candidates=[]
    for term,row in groups.items():
        if len(row["sources"])<min_sources or len(row["documents"])<2:
            continue
        candidates.append({"term":term,"documents":len(row["documents"]),
                           "observed_source_pairs":len(row["sources"]),
                           "publisher_hosts":len(row["hosts"]),
                           "supporting_urls":sorted(row["documents"])[:15],
                           "status":"unreviewed_candidate"})
    candidates.sort(key=lambda x:(-x["publisher_hosts"],-x["documents"],x["term"]))
    return {"schema_version":1,"purpose":"topic_agnostic_candidate_discovery",
            "documents_observed":len(documents),
            "observations_observed":len(observations),
            "candidate_terms":candidates[:max_terms],
            "selection_applied":False,
            "topic_assignment_applied":False,
            "event_clustering_applied":False,
            "limitations":[
                "Term overlap is lexical and not semantic or multilingual clustering.",
                "Source pairs and publisher hosts are not verified independent origins.",
                "The source registry defines a coverage boundary, not a global firehose.",
                "Candidate frequency is not factual credibility or importance.",
                "No automatic topic association or publication is performed."]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("snapshots",nargs="+",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--min-sources",type=int,default=2)
    parser.add_argument("--max-terms",type=int,default=60)
    args=parser.parse_args()
    snapshots=[(str(p),json.loads(p.read_text(encoding="utf-8"))) for p in args.snapshots]
    manifest=federate(snapshots)
    result=global_candidates(manifest,min_sources=args.min_sources,max_terms=args.max_terms)
    result["acquisition_errors"]=manifest["errors"]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("candidate_terms","limitations")},ensure_ascii=False))
if __name__=="__main__":
    main()
