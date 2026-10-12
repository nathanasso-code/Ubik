"""Manual, bounded topic social discovery run; never seed with target news event."""
import argparse
import json
from pathlib import Path
from .topic_social_discovery import discover
from .topic_discovery_diagnostics import diagnose

def main():
    p=argparse.ArgumentParser()
    p.add_argument("topic")
    p.add_argument("--alias",action="append",default=[])
    p.add_argument("--instance",action="append",default=[])
    p.add_argument("--limit",type=int,default=20)
    p.add_argument("--live",action="store_true")
    p.add_argument("--expand",action="store_true")
    p.add_argument("--document-expansion",action="store_true")
    p.add_argument("--max-document-terms",type=int,default=6)
    p.add_argument("--max-expansion-terms",type=int,default=8)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    if not 1<=args.limit<=40:
        p.error("Limit must be 1..40")
    if not args.live:
        print(json.dumps({"status":"dry_run","topic":args.topic,"aliases":args.alias,
                          "network_calls":0},ensure_ascii=False))
        return
    result=discover(args.topic,args.alias,instances=tuple(args.instance or ["mastodon.social"]),
                    limit=args.limit,expand=args.expand,max_expansion_terms=args.max_expansion_terms,
                    document_expansion=args.document_expansion,max_document_terms=args.max_document_terms)
    result["diagnostics"]=diagnose(result)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
