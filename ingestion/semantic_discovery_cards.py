"""Render semantic discovery cards from frozen neighbor evidence, not inferred facts."""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit

def build_semantic_cards(review,*,max_cards=24):
    if not 1<=max_cards<=100:raise ValueError("Invalid card budget")
    cards=[];used=set()
    for item in review.get("selected",[]):
        left=item.get("left") or {};right=item.get("right") or {}
        if not all(isinstance(d.get("url"),str) and urlsplit(d["url"]).scheme in ("http","https")
                   and isinstance(d.get("title"),str) and d["title"].strip()
                   for d in (left,right)):continue
        if left["url"]==right["url"]:continue
        key=tuple(sorted([left["url"],right["url"]]))
        if key in used:continue
        used.add(key)
        cards.append({"id":f"semantic-review-{item.get('frozen_rank',len(cards)+1)}",
                      "type":"semantic_discovery",
                      "title":"Documenti potenzialmente collegati",
                      "status":"da_verificare",
                      "relation":"similarita_semantica_non_validata",
                      "editorial_question":"Descrivono lo stesso evento, un contesto condiviso o eventi distinti?",
                      "sources":[{"url":d["url"],"publisher_host":d.get("host"),
                                  "original_title":d["title"]} for d in (left,right)],
                      "retrieval":{"frozen_rank":item.get("frozen_rank"),
                                   "cosine_similarity":item.get("similarity"),
                                   "score_interpretation":"ranking_only_not_truth_probability"},
                      "claims_verified":False,"same_event_verified":False,
                      "automatic_topic_assignment":False})
        if len(cards)>=max_cards:break
    return {"schema_version":1,"purpose":"review_only_semantic_card_preview",
            "cards":cards,"published":False,"automatic_topic_creation":False,
            "limitations":["Feed titles have not been fact-checked.",
                           "Similarity cannot prove same event, agreement, contradiction or causality.",
                           "No source-text evidence was reviewed.",
                           "Not connected to production topic cards."]}

def render_markdown(result):
    lines=["# Ubik — anteprima card semantiche","",
           "**Solo revisione.** Nessuna relazione fattuale è stata validata.",""]
    for i,card in enumerate(result["cards"],1):
        lines.extend([f"## {i}. {card['title']}",
                      f"**Stato:** {card['status']} · **Posizione originaria:** {card['retrieval']['frozen_rank']}",
                      f"**Somiglianza (non probabilità di verità):** {card['retrieval']['cosine_similarity']}",""])
        for source in card["sources"]:
            title=source["original_title"].replace("[","\\[").replace("]","\\]")
            lines.append(f"- [{title}](<{source['url']}>) — {source['publisher_host']}")
        lines.extend(["",f"**Domanda editoriale:** {card['editorial_question']}",""])
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("review",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path)
    a=p.parse_args()
    result=build_semantic_cards(json.loads(a.review.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if a.markdown:
        a.markdown.parent.mkdir(parents=True,exist_ok=True)
        a.markdown.write_text(render_markdown(result),encoding="utf-8")
    print(json.dumps({"cards":len(result["cards"]),"published":False,"verified":0}))
if __name__=="__main__":main()
