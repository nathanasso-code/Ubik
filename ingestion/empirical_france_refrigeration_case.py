"""Empirical French refrigeration cyberattack: short attributed excerpts only.

Curated from public Reuters, AFP and Euronews reporting on 12 October 2026.
Agency syndication is NOT independent confirmation. No full article is stored.
"""
import json
from pathlib import Path
from ingestion.curated_evidence_merge import assemble_case

OBSERVATIONS=[
 {"event_key":"france-refrigeration-cyberattack-2026-10-12",
  "url":"https://www.reuters.com/business/retail-consumer/french-supermarket-chain-intermarche-hit-by-cyberattack-150-stories-targeted-2026-10-12/",
  "publisher":"Reuters","origin_group":"Reuters","observed_at":"2026-10-12",
  "claim_key":"intermarche_affected_stores","value":{"estimate":150,"scope":"Intermarche alone"},
  "claim":"Reuters attributed approximately 150 affected Intermarché stores to Les Mousquetaires.",
  "evidence_excerpt":"around 150 of its stores had been hit"},
 {"event_key":"france-refrigeration-cyberattack-2026-10-12",
  "url":"https://www.afp.com/en/french-supermarket-chains-say-cyberattack-forced-refrigerator-shutdown",
  "publisher":"AFP","origin_group":"AFP","observed_at":"2026-10-12",
  "claim_key":"intermarche_affected_stores","value":{"range":[150,200],"scope":"Intermarche alone"},
  "claim":"AFP's early report estimated 150–200 Intermarché shops targeted.",
  "evidence_excerpt":"Some 150-200 Intermarche shops were targeted"},
 {"event_key":"france-refrigeration-cyberattack-2026-10-12",
  "url":"https://www.euronews.com/2026/10/12/hundreds-of-french-supermarkets-hit-by-cyberattack-on-refrigeration-systems",
  "publisher":"Euronews","origin_group":"AFP-derived reporting; independence unverified",
  "observed_at":"2026-10-12T16:19:00+02:00",
  "claim_key":"intermarche_affected_stores","value":{"range":[150,200],"scope":"Intermarche alone"},
  "claim":"Euronews repeated the 150–200 Intermarché estimate and nearly 100 Coopérative U stores.",
  "evidence_excerpt":"Around 150 to 200 Intermarché stores were hit"},
 {"event_key":"france-refrigeration-cyberattack-2026-10-12",
  "url":"https://www.reuters.com/business/retail-consumer/french-supermarket-chain-intermarche-hit-by-cyberattack-150-stories-targeted-2026-10-12/",
  "publisher":"Reuters","origin_group":"Reuters","observed_at":"2026-10-12",
  "claim_key":"carrefour_affected_stores","value":80,
  "claim":"Reuters attributed a figure of 80 affected supermarkets to Carrefour.",
  "evidence_excerpt":"Carrefour said 80 of its supermarkets had been hit"}
]

def build():
    case=assemble_case(OBSERVATIONS)
    case["semantic_category"]={"category":"Tecnologia e sicurezza","classification":"curated_rule",
                               "new_topic_created":False}
    case["editorial_synthesis_it"]=(
        "Un attacco informatico ha alterato i sistemi di refrigerazione di supermercati francesi, "
        "provocando perdite alimentari. Reuters riporta circa 150 punti vendita Intermarché "
        "colpiti; AFP ne indica 150–200. I valori sono stime compatibili, non una contraddizione "
        "dimostrata. Carrefour ha riferito 80 punti vendita coinvolti: è una catena diversa "
        "e il numero non va confrontato direttamente con quello di Intermarché. "
        "La ricostruzione delle cause tecniche e l'indipendenza delle fonti restano da verificare.")
    case["full_article_texts_acquired_by_approved_fetcher"]=0
    case["data_basis"]="short_attributed_public_source_excerpts_curated_from_web"
    case["editorial_synthesis_is_automatically_verified"]=False
    return case

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    result=build()
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"observations":len(result["observations"]),"full_texts_fetched":0,
                      "publication_approved":False}))
if __name__=="__main__":main()
