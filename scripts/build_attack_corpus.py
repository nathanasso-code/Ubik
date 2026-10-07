#!/usr/bin/env python3
"""Build the public-facing Ubik attack corpus from conservative UCDP routes."""
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/"data"/"ucdp"; OUT=ROOT/"data"/"ukraine-attacks-derived.json"
def load(n): return json.loads((D/n).read_text(encoding="utf-8"))
def key(e):
 try:return (e.get("date"),round(float(e["lat"]),3),round(float(e["lon"]),3))
 except:return (e.get("date"),e.get("place"),e.get("ucdp_id"))
def canon(e,kind):
 src=str(e.get("source_article") or "").strip()
 return {
  "id":"ucdp-"+str(e.get("ucdp_id")),
  "date":e.get("date"),"date_end":e.get("date_end"),
  "place":e.get("place"),"region":e.get("region"),
  "lat":float(e["lat"]),"lon":float(e["lon"]),
  "type":"long_range_strike" if kind=="long_range" else "civilian_harm",
  "status":"reported",
  "validation":"not_ubik_validated",
  "actor_a":e.get("side_a"),"actor_b":e.get("side_b"),
  "fatalities":{"best":int(e.get("best") or 0),"low":int(e.get("low") or 0),"high":int(e.get("high") or 0)},
  "geo_precision":e.get("geo_precision"),
  "sources":[{"publisher":"UCDP","dataset":e.get("dataset"),"record_id":str(e.get("ucdp_id")),
              "underlying_citation":src,"source_office":e.get("source_office"),
              "number_of_sources":e.get("number_of_sources")}],
  "provenance":{"provider":"UCDP","route":kind,"license":"CC BY 4.0"}
 }
def main():
 lr=load("long_range_candidates.json"); civ=load("civilian_unique.json")
 merged={}; overlaps=0
 for kind,rows in (("long_range",lr),("one_sided_civilian",civ)):
  for e in rows:
   k=key(e)
   if k in merged:
    overlaps+=1
    merged[k]["sources"].extend(canon(e,kind)["sources"])
    merged[k]["provenance"]["merged_routes"]=sorted(set(merged[k]["provenance"].get("merged_routes",[])+[kind]))
   else: merged[k]=canon(e,kind)
 events=sorted(merged.values(),key=lambda x:(x.get("date") or "",x["id"]),reverse=True)
 doc={"schema_version":"2.0","generated_at":datetime.now(timezone.utc).isoformat(),
      "scope":{"country":"Ukraine","from":"2022-02-24",
       "description":"Conservative UCDP-derived candidates for the Ubik Attacks view; not a complete census and not Ubik-validated."},
      "counts":{"events":len(events),"long_range_input":len(lr),"civilian_unique_input":len(civ),"merged_duplicates":overlaps},
      "events":events}
 OUT.write_text(json.dumps(doc,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
 print(json.dumps(doc["counts"]))
if __name__=="__main__":main()
