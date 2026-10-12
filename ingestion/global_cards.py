"""Evidence-linked discovery cards. No generated factual claims or automatic event merges.

Cards are views over publisher-provided feed titles and source links; a review
pair is a navigational suggestion, not a verified common event.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

def build_cards(snapshot,pairs,*,max_cards=24):
    if not 1<=max_cards<=100:raise ValueError("Invalid card budget")
    docs={}
    for item in snapshot.get("items",[]):
        url=item.get("url")
        if not isinstance(url,str) or urlsplit(url).scheme not in ("http","https"):continue
        if not item.get("title"):continue
        docs.setdefault(url,{"url":url,"publisher_title":item["title"],
                            "source_id":item.get("source_id"),
                            "published_raw":item.get("published_raw"),
                            "attribution":"publisher_feed_unverified"})
    cards=[];covered=set()
    for pair in pairs.get("candidate_pairs",[]):
        urls=[d.get("url") for d in pair.get("documents",[])]
        if len(urls)!=2 or urls[0]==urls[1] or any(u not in docs for u in urls):continue
        if any(u in covered for u in urls):continue
        cards.append({"type":"possible_shared_event","review_status":"unverified",
                      "heading":"Possible related reports — review required",
                      "documents":[docs[u] for u in urls],
                      "evidence":{"shared_title_terms":pair.get("shared_title_terms",[]),
                                  "weighted_title_jaccard":pair.get("weighted_title_jaccard"),
                                  "publication_gap_hours":pair.get("publication_gap_hours")},
                      "claim":"No claim of same event or factual accuracy"})
        covered.update(urls)
        if len(cards)>=max_cards:break
    # Show remaining publisher items as explicitly single-source cards.
    for url,d in docs.items():
        if len(cards)>=max_cards:break
        if url not in covered:
            cards.append({"type":"source_document","review_status":"unverified",
                          "heading":d["publisher_title"],"documents":[d],
                          "claim":"Publisher-provided title; not independently verified"})
    return {"schema_version":1,"purpose":"source_grounded_discovery_preview",
            "cards":cards,"total_source_documents":len(docs),
            "automated_summaries":False,"verified_events":False,
            "topic_assignment_applied":False,
            "limitations":[
                "Titles are copied from publisher feeds, not independent fact checks.",
                "Possible shared events require human review; no automatic merging.",
                "Only documents observed in this snapshot can appear.",
                "Cards do not represent a comprehensive news ranking."]}

def render_markdown(result):
    lines=["# Ubik — discovery cards (unverified preview)","",
           "All headings are publisher feed titles or review labels. No generated factual synthesis.",""]
    for i,card in enumerate(result["cards"],1):
        lines.append(f"## {i}. {card['heading']}")
        lines.append(f"**Type:** {card['type']} · **Status:** {card['review_status']}")
        for d in card["documents"]:
            # Escape markdown metacharacters in publisher titles and URL angle brackets.
            title=d["publisher_title"].replace("\\","\\\\").replace("[","\\[").replace("]","\\]")
            lines.append(f"- {title} — {d['source_id']} — <{d['url']}>")
        if card["type"]=="possible_shared_event":
            lines.append("**Why proposed:** overlapping title terms: "+
                         ", ".join(card["evidence"]["shared_title_terms"]))
            lines.append("**Not verified as the same event.**")
        lines.append("")
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("snapshot",type=Path)
    p.add_argument("pairs",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    p.add_argument("--max-cards",type=int,default=24)
    a=p.parse_args()
    result=build_cards(json.loads(a.snapshot.read_text(encoding="utf-8")),
                       json.loads(a.pairs.read_text(encoding="utf-8")),max_cards=a.max_cards)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    a.markdown.parent.mkdir(parents=True,exist_ok=True)
    a.markdown.write_text(render_markdown(result),encoding="utf-8")
    print(json.dumps({"cards":len(result["cards"]),
                      "possible_shared_event_cards":sum(x["type"]=="possible_shared_event" for x in result["cards"]),
                      "single_document_cards":sum(x["type"]=="source_document" for x in result["cards"])}))
    for card in result["cards"][:8]:
        print(json.dumps({"type":card["type"],"heading":card["heading"],
                          "documents":[{"title":x["publisher_title"],"url":x["url"]} for x in card["documents"]]},
                         ensure_ascii=False))
if __name__=="__main__":main()
