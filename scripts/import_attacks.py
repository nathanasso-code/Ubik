#!/usr/bin/env python3
"""Ubik batch event importer.
Usage:
  python scripts/import_attacks.py input.csv
  python scripts/import_attacks.py input.json
Writes normalized, deduplicated events to data/ukraine-attacks.json.
"""
import csv,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"ukraine-attacks.json"

def val(r,*keys):
    for k in keys:
        if k in r and r[k] not in (None,""): return r[k]
    return ""

def fnum(v):
    try:return float(v)
    except:return None

def normalize(r):
    # Native Ubik, ACLED-compatible aliases, and explicit UCDP GED/Candidate mapping.
    is_ucdp = bool(val(r,"where_coordinates","side_a","side_b","type_of_violence"))
    date=str(val(r,"date","event_date"))[:10]
    place=str(val(r,"place","location","where_coordinates"))
    region=str(val(r,"region","admin1","adm_1"))
    lat=fnum(val(r,"lat","latitude")); lon=fnum(val(r,"lon","longitude"))
    typ=str(val(r,"type","sub_event_type","event_type","type_of_violence"))
    target=str(val(r,"target","civilian_targeting","tags"))
    source=str(val(r,"source","publisher","source_article"))
    source_url=str(val(r,"source_url","url"))
    notes=str(val(r,"summary","notes","source_headline"))
    external=str(val(r,"external_id","event_id_cnty","id"))
    if not external:
        external=hashlib.sha1(f"{date}|{place}|{lat}|{lon}|{typ}|{notes[:120]}".encode()).hexdigest()[:16]
    if not all([date,place]) or lat is None or lon is None:return None
    # Geographic guardrail: broad internationally-recognized Ukraine envelope.
    if not (43.0<=lat<=53.0 and 21.0<=lon<=41.5):return None
    return {
      "id":"ua-"+external.lower().replace(" ","-"),"date":date,"place":place,"region":region,
      "lat":lat,"lon":lon,"type":typ or "conflict event","target":target or "unspecified",
      "status":str(val(r,"status")) or ("reported" if is_ucdp else "signal"),"summary":notes or typ or "Imported conflict event",
      "fatalities":int(float(val(r,"fatalities","best") or 0)),
      "fatalities_low":int(float(val(r,"low") or 0)) if is_ucdp else None,
      "fatalities_high":int(float(val(r,"high") or 0)) if is_ucdp else None,
      "actor_a":str(val(r,"actor_a","side_a")),"actor_b":str(val(r,"actor_b","side_b")),
      "geo_precision":str(val(r,"geo_precision","where_prec")),
      "dataset":"UCDP" if is_ucdp else (str(val(r,"dataset")) or "import"),
      "sources":[{"publisher":"UCDP" if is_ucdp else (source or "import"),"url":source_url,"citation":source if is_ucdp else ""}]}

def key(e):
    # Conservative first-pass duplicate key; provenance is merged, not discarded.
    return (e["date"],round(e["lat"],3),round(e["lon"],3),e["type"].lower())

def load_input(p):
    if p.suffix.lower()==".csv":
        with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
    obj=json.loads(p.read_text(encoding="utf-8"))
    return obj.get("data",obj.get("events",obj)) if isinstance(obj,dict) else obj

def main():
    if len(sys.argv)<2:raise SystemExit("Usage: import_attacks.py <csv|json>")
    raw=load_input(Path(sys.argv[1]))
    scoped=[]
    for r in raw:
        country=str(val(r,"country")).strip().lower()
        date=str(val(r,"date","event_date"))[:10]
        if country and country!="ukraine": continue
        if date and date<"2022-02-24": continue
        scoped.append(r)
    incoming=[x for x in (normalize(r) for r in scoped) if x]
    corpus=json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"schema_version":"1.0","events":[]}
    merged={key(e):e for e in corpus.get("events",[])}
    added=combined=0
    for e in incoming:
        k=key(e)
        if k in merged:
            seen={(s.get("publisher"),s.get("url")) for s in merged[k].get("sources",[])}
            for s in e["sources"]:
                if (s.get("publisher"),s.get("url")) not in seen: merged[k].setdefault("sources",[]).append(s)
            combined+=1
        else: merged[k]=e;added+=1
    corpus["events"]=sorted(merged.values(),key=lambda x:x["date"],reverse=True)
    corpus["count"]=len(corpus["events"])
    OUT.write_text(json.dumps(corpus,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"input":len(incoming),"added":added,"merged":combined,"total":len(corpus["events"])}))

if __name__=="__main__":main()
