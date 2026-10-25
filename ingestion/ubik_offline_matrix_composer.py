"""Offline composition of frozen v4 extraction and level-2 pair judgments.
Usage: python -m ingestion.ubik_offline_matrix_composer V4_JSON JUDGMENTS_JSON OUTPUT_JSON
No model calls; never use the evaluation gold as input.
"""
import json
import sys

def compose(v4, level2):
    events, news, assignments = {}, {}, {}
    for source in v4["sources"]:
        sid = source["source_id"]
        for event in source["events"]:
            events[event["qualified_id"]] = event
        for item in source["news"]:
            news[item["key"]] = item
        for item in source["assignments"]:
            key = item["news_key"]
            primary = f'{sid}:{item["primary_event_id"]}'
            targets = [f"{sid}:{e}" for e in item.get("reacts_to", [])]
            assert primary in events and all(t in events for t in targets)
            assignments[key] = dict(primary_event=primary, reacts_to=targets)
    assert set(assignments) == set(news)
    judgments = level2["judgments"] + level2.get("supplemental", [])
    positive = {tuple(sorted(j["pair"])) for j in judgments if j["decision"] == "equivalent"}
    distinct = {tuple(sorted(j["pair"])) for j in judgments if j["decision"] == "distinct"}
    uncertain = [j for j in judgments if j["decision"] == "uncertain"]
    similarity = {tuple(sorted(j["pair"])): j.get("similarity", 0) for j in judgments}
    groups = [{eid} for eid in sorted(events)]
    def group_for(eid):
        return next(g for g in groups if eid in g)
    # Reproduce the frozen conservative merge policy.
    for pair in sorted(positive, key=lambda p: (-similarity.get(p, 0), p)):
        a, b = group_for(pair[0]), group_for(pair[1])
        if a is b:
            continue
        cross = [tuple(sorted((x, y))) for x in a for y in b]
        if any(p in distinct for p in cross):
            continue
        if (len(a) == len(b) == 1) or sum(p in positive for p in cross) >= 2:
            groups.remove(a)
            groups.remove(b)
            groups.append(a | b)
    cards, event_to_card = {}, {}
    for group in sorted(groups, key=lambda g: min(g)):
        members = sorted(group)
        cid = "card:" + members[0]
        cards[cid] = dict(id=cid, events=members, news=[], sources=sorted({e.split(":")[0] for e in members}))
        for eid in members:
            event_to_card[eid] = cid
    for key, item in assignments.items():
        cards[event_to_card[item["primary_event"]]]["news"].append(key)
    for card in cards.values():
        card["news"].sort()
    matrices = {}
    links = []
    for key, item in sorted(assignments.items()):
        origin = event_to_card[item["primary_event"]]
        for target in item["reacts_to"]:
            anchor = event_to_card[target]
            link = dict(news_key=key, source_card=origin, target_card=anchor,
                        target_event=target, relation="reacts_to", provenance="level1_v4")
            links.append(link)
            matrix = matrices.setdefault(anchor, dict(id="matrix:"+anchor, anchor_card=anchor,
                                                       reaction_cards=[], reaction_links=[]))
            matrix["reaction_links"].append(link)
            if origin != anchor and origin not in matrix["reaction_cards"]:
                matrix["reaction_cards"].append(origin)
    for matrix in matrices.values():
        matrix["reaction_cards"].sort()
    reaction_only = sorted({cid for m in matrices.values() for cid in m["reaction_cards"] if cid not in matrices})
    autonomous = sorted(set(cards) - set(matrices) - set(reaction_only))
    uncertain_links = [dict(from_card=event_to_card[j["pair"][0]], to_card=event_to_card[j["pair"][1]],
                            from_event=j["pair"][0], to_event=j["pair"][1],
                            relation="uncertain", provenance="level2",
                            reason=j.get("reason", "")) for j in uncertain]
    assert len(links) == sum(len(a["reacts_to"]) for a in assignments.values())
    assert sum(len(c["events"]) for c in cards.values()) == len(events)
    assert sum(len(c["news"]) for c in cards.values()) == len(news)
    assert len(matrices) + len(reaction_only) + len(autonomous) == len(cards)
    return dict(metadata=dict(event_count=len(events), news_count=len(news), card_count=len(cards),
                              matrix_count=len(matrices), reaction_only_card_count=len(reaction_only),
                              autonomous_card_count=len(autonomous), reaction_link_count=len(links),
                              uncertain_link_count=len(uncertain_links), new_llm_calls=0, gold_used=False),
                cards=cards, matrices=matrices, reaction_only_cards=reaction_only,
                autonomous_cards=autonomous, reaction_links=links,
                uncertain_links=uncertain_links, distinct_pairs=[list(p) for p in sorted(distinct)])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    with open(sys.argv[1]) as f:
        source = json.load(f)
    with open(sys.argv[2]) as f:
        judgments = json.load(f)
    result = compose(source, judgments)
    with open(sys.argv[3], "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result["metadata"], indent=2))
