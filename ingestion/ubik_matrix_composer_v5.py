"""Ubik v5 offline matrix composition. No LLM calls. Relations must be explicit."""
from collections import defaultdict

def compose_v5(cards, relations, conflicts=()):
    by_id = {c["id"]: dict(c) for c in cards}
    if len(by_id) != len(cards):
        raise ValueError("Duplicate card id")
    parents = defaultdict(set)
    reactions = []
    for rel in relations:
        source, target, kind = rel["source"], rel["target"], rel["type"]
        if source not in by_id or target not in by_id:
            raise ValueError("Unknown relation endpoint")
        if source == target:
            raise ValueError("Self relation")
        if kind == "part_of":
            parents[source].add(target)
        elif kind == "reacts_to":
            reactions.append(rel)
        else:
            raise ValueError("Unknown relation")
    def ancestors(card_id, seen=None):
        seen = set() if seen is None else seen
        if card_id in seen:
            raise ValueError("Cyclic part_of")
        if not parents[card_id]:
            return {card_id}
        return set().union(*(ancestors(p, seen | {card_id}) for p in parents[card_id]))
    memberships = {cid: sorted(ancestors(cid)) for cid in by_id}
    matrices = {}
    for root in sorted({r for roots in memberships.values() for r in roots}):
        members = sorted(cid for cid, roots in memberships.items() if root in roots)
        matrices[root] = {"id": "matrix:" + root, "anchor_card": root,
                          "cards": members,
                          "part_of": [r for r in relations if r["type"] == "part_of"
                                      and r["source"] in members and r["target"] in members],
                          "reactions": [r for r in reactions if r["target"] in members]}
    return {"cards": cards, "matrices": list(matrices.values()),
            "memberships": memberships, "reactions": reactions,
            "conflicts": list(conflicts), "new_llm_calls": 0}
