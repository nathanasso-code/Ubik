"""Bounded global RSS metadata collection, independent of topic seeds.

Reuses the established feed parser and HTTP protections, but does not inherit
the AI-specific topic label, historical cache, or arXiv fallback behavior.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
from xml.etree.ElementTree import ParseError
from scripts.discover_ai_sources import parse_feed, fetch

def collect(registry,output,fetcher=fetch,*,max_sources=40,max_items_per_source=80):
    config=json.loads(Path(registry).read_text(encoding="utf-8"))
    if config.get("purpose")!="global_topic_agnostic_rss":
        raise ValueError("Expected explicit global source registry")
    if not 1<=max_sources<=40 or not 1<=max_items_per_source<=200:
        raise ValueError("Invalid collection limits")
    sources=[s for s in config.get("sources",[]) if s.get("enabled") and s.get("kind")=="rss"]
    if len(sources)>max_sources:
        raise ValueError("Registry exceeds source budget")
    items=[]; reports=[]
    for source in sources:
        try:
            discovered=parse_feed(fetcher(source["url"]),source)[:max_items_per_source]
            for row in discovered:
                row["topic_ids"]=[]
                row["discovery_mode"]="global_unassigned"
            items.extend(discovered)
            reports.append({"source_id":source["id"],"status":"ok","items":len(discovered)})
        except (ValueError,OSError,TimeoutError,ParseError) as exc:
            reports.append({"source_id":source["id"],"status":"error","error_type":type(exc).__name__})
    result={"schema_version":1,"purpose":"global_topic_agnostic_rss",
            "retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),
            "items":items,"source_reports":reports,
            "coverage":{"configured_sources":len(sources),
                        "successful_sources":sum(r["status"]=="ok" for r in reports),
                        "observations":len(items),
                        "distinct_url_hints":len({r["url"] for r in items})}}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registry",type=Path,default=Path("config/source-registry.global-pilot.json"))
    p.add_argument("--output",type=Path,default=Path("data/discovery/global-rss-pilot.json"))
    a=p.parse_args()
    r=collect(a.registry,a.output)
    print(json.dumps(r["coverage"],ensure_ascii=False))
    if r["coverage"]["successful_sources"]==0:
        raise SystemExit("No successful sources")
if __name__=="__main__":
    main()
