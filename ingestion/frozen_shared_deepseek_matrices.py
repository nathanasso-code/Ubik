"""Paired Qwen/DeepSeek grouping on frozen DeepSeek extraction; matrix candidates from original embedding components."""
import argparse, json, os
from pathlib import Path
from collections import defaultdict
from ingestion.frozen_independent_qwen_deepseek import REVIEW, ask

def build_matrices(context, cards):
    """Preserve embedding provenance; never conflate connectedness with validated topic identity."""
    owner = {nid: i for i, comp in enumerate(context["embedding_components"]) for nid in comp}
    grouped = defaultdict(list)
    for card in cards:
        components = {owner[n] for n in card["news_ids"]}
        if len(components) != 1:
            raise ValueError("Card spans embedding components")
        grouped[next(iter(components))].append(card)
    matrices = []
    for component_id, members in sorted(grouped.items()):
        source_to_cards = defaultdict(set)
        for card in members:
            for s in card["sources"]:
                source_to_cards[s["source_id"]].add(card["id"])
        shared = {s: sorted(ids) for s, ids in source_to_cards.items() if len(ids) > 1}
        matrices.append({
            "id": f"matrix-{context['context']}-{component_id}",
            "embedding_component": component_id,
            "candidate_only": True,
            "news_ids": context["embedding_components"][component_id],
            "card_ids": [c["id"] for c in members],
            "sources": sorted(source_to_cards),
            "shared_sources_across_cards": shared,
            "needs_coherence_review": len(members) > 1,
            "title_candidate": members[0]["title"],
        })
    return matrices

def main():
    p = argparse.ArgumentParser()
    p.add_argument("prior_results", type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    prior = json.loads(args.prior_results.read_text())
    original = prior["arms"]["B_deepseek"]
    output = {"experiment":"same_deepseek_extraction_qwen_vs_deepseek_review",
              "source_experiment": prior["experiment"], "arms": {}}
    for arm, model in [("A_qwen",os.environ["UBIK_QWEN_MODEL"]),
                       ("B_deepseek",os.environ["UBIK_LLM_MODEL"])]:
        result = {"model":model,"contexts":[],"errors":[],"usage":{"calls":0}}
        for context in original["contexts"]:
            news = {s["news_id"]:s for card in context["cards"] for s in card["sources"]}
            cards = []
            for index, component in enumerate(context["embedding_components"]):
                payload = [{"id":nid,"title":news[nid]["original_title"],
                            "summary":news[nid]["summary"],"source_id":news[nid]["source_id"]}
                           for nid in component]
                if len(component) == 1:
                    groups = [{"ids":component,"title":payload[0]["title"],
                               "summary":payload[0]["summary"],"reason":"singleton"}]
                else:
                    try:
                        response = ask(model,REVIEW,{"news":payload},result["usage"])
                        groups = response["groups"]
                        ids = [nid for g in groups for nid in g["ids"]]
                        if sorted(ids) != sorted(component) or len(ids) != len(set(ids)):
                            raise ValueError("Review must partition component exactly once")
                    except Exception as e:
                        result["errors"].append({"context":context["context"],
                            "component":index,"error":str(e)[:300]})
                        groups = [{"ids":[nid],"title":news[nid]["original_title"],
                                   "summary":news[nid]["summary"],"reason":"review_failed"}
                                  for nid in component]
                for g in groups:
                    ids = g["ids"]
                    cards.append({"id":f"{arm}-{context['context']}-{len(cards)}",
                                  "news_ids":ids,"title":g.get("title") or news[ids[0]]["original_title"],
                                  "summary":g.get("summary") or news[ids[0]]["summary"],
                                  "reason":g.get("reason"),
                                  "sources":[news[nid] for nid in ids]})
            matrices = build_matrices(context,cards)
            result["contexts"].append({"context":context["context"],
                "input_count":len(news),"embedding_components":context["embedding_components"],
                "cards":cards,"matrix_candidates":matrices})
        result["totals"] = {"cards":sum(len(c["cards"]) for c in result["contexts"]),
            "matrix_candidates":sum(len(c["matrix_candidates"]) for c in result["contexts"]),
            "multi_card_candidates":sum(sum(len(m["card_ids"])>1 for m in c["matrix_candidates"]) for c in result["contexts"]),
            "shared_source_links":sum(sum(len(m["shared_sources_across_cards"]) for m in c["matrix_candidates"]) for c in result["contexts"])}
        output["arms"][arm]=result
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2))
    print(json.dumps({k:v["totals"] for k,v in output["arms"].items()}))
if __name__=="__main__": main()
