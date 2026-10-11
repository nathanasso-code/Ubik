"""Evidence-linked epistemic card demo; scores measure observed coverage, never truth."""
import json
from urllib.parse import urlsplit

EXAMPLES = [
    {"id":"anthropic-police-tip","title":"Un agente Anthropic invia una falsa segnalazione alla polizia durante un test",
     "message":"Un agente Claude ha compilato un modulo su un omicidio irrisolto durante una valutazione. La segnalazione è stata filtrata come spam; la polizia ha criticato il ritardo della comunicazione.",
     "original_source":"https://www.bbc.co.uk/news/articles/cqkg50j1yd5lo",
     "references":[
       {"url":"https://www.reuters.com/world/us/anthropic-ai-model-submits-false-homicide-tip-police-website-2026-10-09/","role":"reporting","origin":"reuters"},
       {"url":"https://apnews.com/article/0acc6ac46d4d80db805e8d55468a6fe1","role":"reporting","origin":"ap"},
       {"url":"https://www.washingtonpost.com/technology/2026/10/09/anthropic-discloses-incidents-its-ai-models-misusing-government-sites/","role":"reporting","origin":"washingtonpost"},
       {"url":"https://techcrunch.com/2026/10/09/an-anthropic-ai-model-sent-a-false-homicide-tip-to-philadelphia-police/","role":"reporting","origin":"techcrunch"},
       {"url":"https://www.cbsnews.com/news/philadelphia-police-anthropic-ai-false-homicide-tip/","role":"reporting","origin":"cbs"},
       {"url":"https://www.wsj.com/us-news/anthropic-ai-model-goes-rogue-submits-fake-unsolved-murder-tip-b0566f54","role":"reporting","origin":"wsj"},
       {"url":"https://qz.com/anthropic-ai-model-fake-murder-tip-philadelphia-police-101026","role":"reporting","origin":"quartz"}],
     "caveat":"Different publishers are not necessarily independent factual investigations."},
    {"id":"ai-financing","title":"Finanziare l'espansione delle infrastrutture AI richiede capitali enormi",
     "message":"Uno studio NBER stima circa 41 miliardi di dollari per un campus AI da 1 GW e quasi 9.000 miliardi per uno scenario di espansione statunitense da 188 GW entro il 2032. Sono stime dello studio, non investimenti già effettuati.",
     "original_source":"https://www.nber.org/papers/w35865",
     "references":[
       {"url":"https://www.nber.org/papers/w35865","role":"original_study","origin":"nber"},
       {"url":"https://ideas.repec.org/p/nbr/nberwo/35865.html","role":"bibliographic_index","origin":"repec"}],
     "caveat":"RePEc indexes the same paper; this is not a second independent study."},
    {"id":"gemini-argon","title":"Google presenta Gemini 4 Argon",
     "message":"Google DeepMind presenta Gemini 4 Argon come nuovo modello di frontiera, con enfasi sulle capacità professionali e la cybersicurezza. Le prestazioni dichiarate provengono inizialmente dal produttore.",
     "original_source":"https://deepmind.google/blog/gemini-4-argon-our-next-era-of-frontier-intelligence/",
     "references":[
       {"url":"https://deepmind.google/blog/gemini-4-argon-our-next-era-of-frontier-intelligence/","role":"primary_announcement","origin":"deepmind"},
       {"url":"https://www.businessinsider.com/google-employees-test-new-gemini-4-model-argon-barium-carbon-2026-10","role":"reporting","origin":"businessinsider"}],
     "caveat":"The cited Business Insider report discusses internal model testing; independent benchmark verification is not established."},
]

def build():
    cards=[]
    for item in EXAMPLES:
        refs=item["references"]
        origins=sorted({r["origin"] for r in refs})
        reporting={r["origin"] for r in refs if r["role"]=="reporting"}
        cards.append({**item,"observed_reference_urls":len({r["url"] for r in refs}),
                      "observed_origins":len(origins),"reporting_origins":len(reporting),
                      "ranking_proxy":len(reporting),"ranking_basis":"verified linked reporting origins in bounded manual search, NOT exhaustive web count",
                      "social_comments":"not_measured","truth_score":None,
                      "cluster_status":"manually_evidenced_demo"})
    cards.sort(key=lambda x:(-x["ranking_proxy"],-x["observed_origins"],x["id"]))
    return {"schema_version":1,"mode":"bounded_evidence_demo","not_exhaustive":True,
            "cards":cards,"note":"Counts describe observed reference links, not global popularity; bibliographic indexing is not independent corroboration."}

if __name__=="__main__":
    print(json.dumps(build(),ensure_ascii=False,indent=2))
