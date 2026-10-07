#!/usr/bin/env python3
"""Conservative second-stage routing of UCDP Ukraine events."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/"data"/"ucdp"

LONG_RANGE=[
 r"\bmissil",r"\bmissile",r"\bcruise missile",r"ballistic missile",r"\brocket attack",
 r"\bdrone",r"\bshahed",r"\buav\b",r"air ?strike",r"aerial attack",
 r"guided (?:air )?bomb",r"glide bomb",r"air bomb"
]
SHELLING=[r"shelling",r"shelled",r"artillery",r"bombard",r"mortar",r"cluster munition"]
GROUND=[
 r"ground assault",r"infantry",r"stormed",r"assault group",r"small arms",r"close combat",
 r"firefight",r"captured (?:the )?(?:village|town|settlement|position)",
 r"seized (?:the )?(?:village|town|settlement|position)"
]
def hits(ps,t): return [p for p in ps if re.search(p,t,re.I)]
def text(e): return " ".join(str(e.get(k) or "") for k in ("source_article","source_office","place","region"))
def main():
 src=json.loads((D/"front_events.json").read_text(encoding="utf-8"))
 civilian=json.loads((D/"attack_candidates.json").read_text(encoding="utf-8"))
 out={"long_range_candidates":[],"shelling_review":[],"ground_front":[],"ambiguous":[]}
 for e in src:
  t=text(e); lr,sh,gr=hits(LONG_RANGE,t),hits(SHELLING,t),hits(GROUND,t)
  if lr and not gr: b="long_range_candidates"; evidence=lr
  elif gr and not lr and not sh: b="ground_front"; evidence=gr
  elif sh and not lr and not gr: b="shelling_review"; evidence=sh
  else: b="ambiguous"; evidence=lr+sh+gr
  e["routing_v2"]={"bucket":b,"matched_signals":evidence[:8]}
  out[b].append(e)
 # Deduplicate civilian one-sided events against state-based events conservatively by date + rounded coords.
 state_keys={(e.get("date"),round(float(e["lat"]),3),round(float(e["lon"]),3)) for e in src if e.get("lat") and e.get("lon")}
 civ_unique=[]; civ_overlap=[]
 for e in civilian:
  try:k=(e.get("date"),round(float(e["lat"]),3),round(float(e["lon"]),3))
  except (ValueError,TypeError):k=None
  (civ_overlap if k in state_keys else civ_unique).append(e)
 out["civilian_unique"]=civ_unique; out["civilian_possible_overlap"]=civ_overlap
 for k,v in out.items():
  (D/(k+".json")).write_text(json.dumps(v,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
 summary={"state_based_input":len(src),"one_sided_civilian_input":len(civilian),
          **{k:len(v) for k,v in out.items()},
          "publication_rule":"long_range_candidates are candidates, not validated events; shelling_review requires front/control context; ambiguous is never auto-published",
          "dedup_rule":"possible overlap = same date and coordinates rounded to 0.001 degrees"}
 (D/"routing-v2-manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(summary))
if __name__=="__main__":main()
