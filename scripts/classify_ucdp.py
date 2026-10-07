#!/usr/bin/env python3
"""Route UCDP state-based Ukraine events using explicit textual evidence only."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/"data"/"ucdp"
STRIKE=[
 r"\bmissil",r"\bmissile",r"\brocket",r"\bdrone",r"\bshahed",r"\buav\b",
 r"air ?strike",r"aerial attack",r"bombard",r"shelling",r"shelled",r"artillery",
 r"guided bomb",r"glide bomb",r"air bomb",r"cluster munition"
]
GROUND=[
 r"ground assault",r"infantry",r"stormed",r"assault group",r"small arms",
 r"close combat",r"firefight",r"captured (?:the )?(?:village|town|settlement|position)",
 r"seized (?:the )?(?:village|town|settlement|position)"
]
def hit(patterns,t):return any(re.search(p,t,re.I) for p in patterns)
def main():
 src=json.loads((D/"front_events.json").read_text(encoding="utf-8"))
 out={"strike_candidates":[],"ground_front":[],"ambiguous":[]}
 for e in src:
  t=" ".join(str(e.get(k) or "") for k in ("source_article","source_office","place","region"))
  s,g=hit(STRIKE,t),hit(GROUND,t)
  if s and not g: bucket="strike_candidates"
  elif g and not s: bucket="ground_front"
  else: bucket="ambiguous"
  e["routing_reason"]="explicit_source_text" if bucket!="ambiguous" else "insufficient_or_conflicting_text"
  out[bucket].append(e)
 for k,v in out.items():
  (D/(k+".json")).write_text(json.dumps(v,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
 summary={"input":len(src),**{k:len(v) for k,v in out.items()},
          "rule":"lexical routing over UCDP source_article/source_office; ambiguous is never auto-published"}
 (D/"routing-manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(summary))
if __name__=="__main__":main()
