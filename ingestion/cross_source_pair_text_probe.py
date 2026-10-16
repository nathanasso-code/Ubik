"""Bounded article-text evidence on candidate pairs, no body persistence.

Only uses original URL and existing robots-respecting probe.
"""
import argparse,collections,json
from pathlib import Path
from ingestion.live_get_text_probe import inspect

def select(pairs,max_pairs=24):
    # Cover strong matches, borderline matches and weaker candidates.
    rows=pairs.get("top_pairs",[])
    groups=[rows[:8],rows[25:33],rows[65:73]]
    result=[];seen=set()
    for group in groups:
        for p in group:
            if len(result)>=max_pairs:break
            key=(p["left"]["url"],p["right"]["url"])
            if key not in seen:result.append(p);seen.add(key)
    return result
def run(data,checker=inspect):
    pairs=select(data)
    urls={side["url"] for pair in pairs for side in (pair["left"],pair["right"])}
    checked={}
    for url in sorted(urls):
        checked[url]=checker(url)
    records=[]
    for pair in pairs:
        left,right=pair["left"],pair["right"]
        a,b=checked[left["url"]],checked[right["url"]]
        def status(x):
            t=x.get("alternative_extractors",{}).get("trafilatura",{})
            return {"fetch_status":x.get("status"),"content_tier":x.get("content_tier"),
                    "trafilatura_chars":t.get("chars",0),"trafilatura_words":t.get("words",0),
                    "text_800_100":bool(t.get("substantial_800")),
                    "text_1200_180":bool(t.get("substantial_1200_180")),
                    "error_type":x.get("error_type")}
        records.append({"score":pair["score"],"left":{**left,**status(a)},
                        "right":{**right,**status(b)},
                        "both_800_100":bool(a.get("alternative_extractors",{}).get("trafilatura",{}).get("substantial_800") and b.get("alternative_extractors",{}).get("trafilatura",{}).get("substantial_800"))})
    summary={"pairs_selected":len(records),"unique_urls_attempted":len(urls),
             "get_success":sum(x.get("status")=="get_success" for x in checked.values()),
             "pairs_both_800_100":sum(x["both_800_100"] for x in records),
             "individual_800_100":sum(bool(x.get("alternative_extractors",{}).get("trafilatura",{}).get("substantial_800")) for x in checked.values()),
             "by_status":dict(collections.Counter(x.get("status") for x in checked.values()))}
    return {"schema_version":1,"method":"robots_checked_live_get_plus_trafilatura",
            "summary":summary,"pairs":records,
            "limitations":["Only access and text-length evidence, not semantic relation classification.",
                           "No article body stored. Access is not publication permission.",
                           "Selected score strata are not a representative random sample."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();result=run(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("Pairwise full-text accessibility:",json.dumps(result["summary"]))
if __name__=="__main__":main()
