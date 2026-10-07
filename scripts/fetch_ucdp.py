#!/usr/bin/env python3
"""Ubik UCDP ingestion. Public CSV by default; token API optional."""
import csv,io,json,os,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data"/"ucdp"; OUT.mkdir(parents=True,exist_ok=True)
PUBLIC={
 "ged":("https://ucdp.uu.se/downloads/ged/ged261-csv.zip","26.1"),
 "candidate":("https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv","26.0.8")
}
def download(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 Ubik research"})
 with urllib.request.urlopen(req,timeout=180) as r:return r.read()
def parse(name,b):
 if name=="ged":
  z=zipfile.ZipFile(io.BytesIO(b)); n=next(x for x in z.namelist() if x.lower().endswith(".csv")); b=z.read(n)
 return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
def s(r,k):return str(r.get(k) or "").strip()
def russian(r):return "russia" in (s(r,"side_a")+" "+s(r,"side_b")).lower()
def route(r):
 if not russian(r):return "other"
 t=s(r,"type_of_violence")
 if t=="3":return "attack_candidates"
 if t=="1":return "front_events"
 return "other"
def compact(r,dataset):
 return {"ucdp_id":r.get("id"),"dataset":dataset,"date":s(r,"date_start")[:10],"date_end":s(r,"date_end")[:10],
 "place":s(r,"where_coordinates"),"region":s(r,"adm_1"),"lat":r.get("latitude"),"lon":r.get("longitude"),
 "geo_precision":r.get("where_prec"),"side_a":s(r,"side_a"),"side_b":s(r,"side_b"),
 "type_of_violence":r.get("type_of_violence"),"best":r.get("best"),"low":r.get("low"),"high":r.get("high"),
 "source_article":s(r,"source_article"),"source_office":s(r,"source_office"),"number_of_sources":r.get("number_of_sources")}
def main():
 canonical={}; releases={}
 for name,(url,version) in PUBLIC.items():
  rows=parse(name,download(url)); kept=0
  for r in rows:
   if s(r,"country").lower()!="ukraine":continue
   d=s(r,"date_start")[:10]
   if d and d<"2022-02-24":continue
   if not r.get("latitude") or not r.get("longitude"):continue
   canonical[str(r.get("id"))]=compact(r,name);kept+=1
  releases[name]={"version":version,"ukraine_rows":kept}
 buckets={"attack_candidates":[],"front_events":[],"other":[]}
 for r in canonical.values():buckets[route(r)].append(r)
 for k,v in buckets.items():
  v.sort(key=lambda x:x["date"],reverse=True)
  (OUT/(k+".json")).write_text(json.dumps(v,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
 manifest={"source":"UCDP public CSV","license":"CC BY 4.0","releases":releases,"ukraine_total":len(canonical),**{k:len(v) for k,v in buckets.items()}}
 (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(manifest))
if __name__=="__main__":main()
