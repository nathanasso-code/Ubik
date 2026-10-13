"""Empirical source-excerpt case; no full-text scraping or republishing."""
import json
from pathlib import Path
from ingestion.curated_evidence_merge import assemble_case,categorize

OBSERVATIONS=[
 {"event_key":"mexico-hurricane-simon-storm-rachel-2026-10",
  "url":"https://efe.com/mundo/2026-10-12/mexico-huracanes-simon-rachel-muertos-danos/",
  "publisher":"EFE","origin_group":"EFE","observed_at":"2026-10-12T12:00:00Z",
  "claim_key":"reported_death_toll","value":2,
  "claim":"EFE reported two deaths, one in Guerrero and one in Baja California, as of its October 12 dispatch.",
  "evidence_excerpt":"Las autoridades mexicanas confirmaron este lunes la primera muerte por el paso del huracán Simón"},
 {"event_key":"mexico-hurricane-simon-storm-rachel-2026-10",
  "url":"https://www.aljazeera.com/news/2026/10/12/two-deaths-reported-as-hurricane-simon-storm-rachel-batter-mexicos-coast",
  "publisher":"Al Jazeera","origin_group":"Al Jazeera / AP syndication","observed_at":"2026-10-12T18:00:00Z",
  "claim_key":"reported_death_toll","value":2,
  "claim":"Al Jazeera reported at least two deaths in its October 12 account, citing authorities and AP.",
  "evidence_excerpt":"At least two people have died in Mexico after Hurricane Simon and former tropical storm Rachel"},
 {"event_key":"mexico-hurricane-simon-storm-rachel-2026-10",
  "url":"https://www.theguardian.com/world/2026/oct/13/mexico-hurricane-simon-tropical-storm-rachel-kill-five-pacific-coast",
  "publisher":"The Guardian","origin_group":"Guardian / AFP / AP agencies","observed_at":"2026-10-13T04:29:00Z",
  "claim_key":"reported_death_toll","value":5,
  "claim":"Guardian and agencies reported at least five deaths, including four family members attributed to Rachel.",
  "evidence_excerpt":"At least five people have died after Hurricane Simon and Tropical Storm Rachel pummelled Mexico’s Pacific coast"},
 {"event_key":"mexico-hurricane-simon-storm-rachel-2026-10",
  "url":"https://apnews.com/article/cc01ec735f4ff7c11798bc9066dc1879",
  "publisher":"Associated Press","origin_group":"AP","observed_at":"2026-10-12T18:00:56Z",
  "claim_key":"reported_death_toll","value":5,
  "claim":"AP reported five deaths and detailed four fatalities in Baja California.",
  "evidence_excerpt":"Hurricane Simon pounded western Mexico with more wind and rain Monday after tropical weather systems caused five deaths"}
]

def build():
    case=assemble_case(OBSERVATIONS)
    case["semantic_category"]=categorize(case)
    case["editorial_synthesis_it"]=(
        "Le fonti consultate descrivono gli effetti congiunti di Simon e Rachel in Messico. "
        "I resoconti citano inizialmente almeno due morti, mentre altre ricostruzioni riportano "
        "cinque vittime, quattro delle quali in Baja California. Le cifre non costituiscono "
        "necessariamente una contraddizione: differiscono il momento del resoconto e i dettagli "
        "disponibili. La cronologia precisa degli aggiornamenti e l'indipendenza delle fonti "
        "richiedono ulteriori verifiche.")
    case["editorial_synthesis_is_automatically_verified"]=False
    case["data_basis"]="short_publicly_visible_source_excerpts_curated_from_web_search"
    case["full_article_texts_acquired_by_approved_fetcher"]=0
    case["real_world_case"]=True
    return case
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    result=build()
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"observations":len(result["observations"]),
                      "potential_updates":len(result["potential_updates"]),
                      "full_texts_fetched":0,"publication_approved":False}))
if __name__=="__main__":main()
