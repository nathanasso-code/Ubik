#!/usr/bin/env python3
"""Fetch current UCDP GED + Candidate and create Ukraine working sets."""
import csv,io,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URLS={
 "ged":"https://ucdp.uu.se/downloads/ged/ged261-csv.zip",
 "candidate":"https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv"
}
UA=ROOT/"data"/"ucdp"
UA.mkdir(parents=True,exist_ok=True)

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Ubik/0.1 research corpus"})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def rows_from_bytes(name,b):
    if name=="ged":
        z=zipfile.ZipFile(io.BytesIO(b))
        csvname=next(n for n in z.namelist() if n.lower().endswith(".csv"))
        text=z.read(csvname).decode("utf-8-sig")
    else:text=b.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))

def ukraine(rows):
    out=[]
    for r in rows:
        if str(r.get("country","")).strip().lower()!="ukraine":continue
        d=str(r.get("date_start") or r.get("date") or "")
        if d and d[:10]<"2022-02-24":continue
        out.append(r)
    return out

def russian_actor(r):
    a=(str(r.get("side_a",""))+" "+str(r.get("side_b",""))).lower()
    return any(x in a for x in ("russia","russian"))

def classify(r):
    # UCDP is lethal-event data. This classification is routing, not Ubik validation.
    if not russian_actor(r):return "other"
    # one-sided violence is an attack candidate; state-based events remain front/battle
    tov=str(r.get("type_of_violence","")).strip()
    if tov=="3":return "attack_candidates"
    return "front_events"

def main():
    combined={}
    for name,url in URLS.items():
        for r in ukraine(rows_from_bytes(name,get(url))):
            rid=str(r.get("id") or "")
            if rid:combined[rid]=r
    buckets={"attack_candidates":[],"front_events":[],"other":[]}
    for r in combined.values():buckets[classify(r)].append(r)
    for k,v in buckets.items():
        (UA/(k+".json")).write_text(json.dumps(v,ensure_ascii=False),encoding="utf-8")
    manifest={"source":"UCDP","license":"CC BY 4.0","ged":"26.1","candidate":"26.0.8",
              "ukraine_total":len(combined),**{k:len(v) for k,v in buckets.items()}}
    (UA/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest))

if __name__=="__main__":main()
