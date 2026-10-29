"""Ukraine v5.1 evaluation against the frozen blind mapping (no model calls).

Scores v5.1 judge outputs, and for comparison the v5 outputs of the same judges recomposed with the
same code. The v5 event mapping below was read from the v5 extraction only (actor, action, object,
evidence), without consulting any judgment, and is declared as constructed after the fact for
comparison.

Usage: python -m ingestion.ubik_ukraine_v51_evaluate V51_DIR V5_EXTRACTION V5_SONNET V5_DEEPSEEK OUT
"""
import collections
import json
import re
import sys

from ingestion.ubik_ukraine_v51_judge import compose

# identity classes: events that the reference expects in one card
CLASS = {"A": "A", "A/A1": "A", "B": "B", "B/B1": "B", "C": "C", "C/C1": "C", "D": "D",
         "A2": "A2", "B2": "B2"}
FAMILY = {"A": ["A", "A/A1", "A2", "A3", "A4"], "B": ["B", "B/B1", "B2"],
          "C": ["C", "C/C1", "C2", "C3", "C4"], "D": ["D", "D1", "D2"]}
V5_MAP = {
    "S188:e1": "B/B1", "S188:e2": "A/A1", "S188:e3": "A6", "S305:e1": "D1", "S305:e2": "D",
    "S382:E1": "C/C1", "S382:E2": "C", "S382:E3": "C2", "S382:E4": "A4", "S382:E5": "A", "S382:E6": "C3",
    "S383:e1": "B/B1", "S383:e2": "A", "S387:e1": "A", "S387:e2": "A", "S387:e3": "A3", "S387:e4": "C",
    "S387:e5": "C4", "S389:e1": "OUT/n22", "S389:e2": "OUT/n23", "S389:e3": "NONE", "S389:e4": "A",
    "S389:e5": "OUT/n24", "S389:e6": "NONE", "S408:e1": "OUT/n26", "S408:e2": "D2", "S408:e3": "D",
    "S408:e4": "OUT/n28", "S408:e5": "A2", "S408:e6": "A", "S408:e7": "X_INDETERMINATE", "S408:e8": "A5",
    "S433:e1": "B/B1", "S433:e2": "B2", "S433:e3": "A", "S433:e4": "A2", "S465:e1": "B2", "S465:e2": "B",
}


def v51_maps(mapping):
    base = {r["extracted_event_id"]: r["reference_id"] for r in mapping["rows"]}
    one = dict(base, **{"S408:e6": "A"})
    two = dict(base, **{"S408:e6": "X_INDETERMINATE"})
    return {"reading_1_e6_is_A": one, "reading_2_e6_excluded": two}


def containers(comp, card):
    inc = comp["memberships"].get(card)
    return [i for i in inc] if inc else ["topic:" + card]


def score(m, judgments, comp, groups):
    card_of = {e: "card:" + g[0] for g in groups for e in g}
    a_core = [e for e, r in m.items() if CLASS.get(r) == "A"]
    b_core = [e for e, r in m.items() if CLASS.get(r) == "B"]
    ab = collections.Counter()
    for j in judgments:
        x, y = j["left"], j["right"]
        if (x in a_core and y in b_core) or (y in a_core and x in b_core):
            ab[j["result"]["decision"]] += 1
    ab_group_merge = [g for g in groups if set(g) & set(a_core) and set(g) & set(b_core)]
    ab_incident_merge = []
    for inc in comp["incidents"]:
        evs = {e for g in groups if "card:" + g[0] in inc["cards"] for e in g}
        if evs & set(a_core) and evs & set(b_core):
            ab_incident_merge.append(inc["id"])
    a_fragments = sorted({c for e in a_core for c in containers(comp, card_of[e])})
    split = {}
    for v, refs in FAMILY.items():
        evs = [e for e, r in m.items() if r in refs]
        split[v] = sorted({c for e in evs for c in containers(comp, card_of[e])})
    false_merges, unverifiable = [], []
    for g in groups:
        classes = {CLASS.get(m[e], m[e]) for e in g}
        if len(classes) > 1:
            (unverifiable if classes & {"X_INDETERMINATE", "A5", "NONE"} else false_merges).append(
                {"group": g, "refs": [m[e] for e in g]})
    card_splits = {}
    for cls in sorted(set(CLASS.values())):
        evs = [e for e, r in m.items() if CLASS.get(r) == cls]
        if len(evs) > 1:
            card_splits[cls] = len({card_of[e] for e in evs}) - 1
    weighted = 2 * sum(len(c) > 1 for c in split.values()) + 3 * len(false_merges) + sum(card_splits.values())
    return {"ab_pair_verdicts": dict(ab), "ab_group_merge": ab_group_merge, "ab_incident_merge": ab_incident_merge,
            "a_fragments": a_fragments, "vicenda_containers": split,
            "vicende_split": [v for v, c in split.items() if len(c) > 1],
            "false_card_merges": false_merges, "unverifiable_merges": unverifiable, "card_splits": card_splits,
            "weighted_error": weighted,
            "weighted_formula": "2 x split vicende (once each) + 3 x false card merges + 1 x extra cards per identity class"}


def eu_reasons(judgments):
    return [{"pair": [j["left"], j["right"]], "reason": j["result"]["reason"][:200]} for j in judgments
            if re.search(r"\bEU\b|European Union", j["result"]["reason"]) and re.search(r"diesel", j["result"]["reason"], re.I)]


def main(v51_dir, v5_extraction, v5_sonnet, v5_deepseek, out_path):
    mapping = json.load(open(f"{v51_dir}/ukraine-v51-blind-mapping.json"))
    report = {"stage": "evaluation", "model_calls": 0, "v51": {}, "v5": {}}
    for arm in ("sonnet", "deepseek"):
        d = json.load(open(f"{v51_dir}/ukraine-v51-judge-{arm}.json"))
        groups = d["assembly"]["groups"]
        report["v51"][arm] = {"status": d["status"], "cost_usd": d["total_cost_usd"],
                              "pipeline_cost_usd": d["total_pipeline_cost_usd"],
                              "invalid_after_retry": len(d["invalid_after_retry"]),
                              "verdicts": dict(collections.Counter(j["result"]["decision"] for j in d["judgments"])),
                              "incidents": len(d["composition"]["incidents"]), "matrices": len(d["composition"]["matrices"]),
                              "eu_diesel_reasons": eu_reasons(d["judgments"]),
                              "judge_part_of": [{"pair": [j["left"], j["right"]], "direction": j["result"]["direction"]}
                                                for j in d["judgments"] if j["result"]["decision"] == "part_of"],
                              "readings": {k: score(m, d["judgments"], d["composition"], groups)
                                           for k, m in v51_maps(mapping).items()}}
    ex5 = json.load(open(v5_extraction))
    ev5 = {s["source_id"] + ":" + e["id"]: e for s in ex5["sources"] for e in s["answer"]["events"]}
    for arm, path in (("sonnet", v5_sonnet), ("deepseek", v5_deepseek)):
        d = json.load(open(path))
        scores = {(j["left"], j["right"]): j["similarity"] for j in d["judgments"]}
        built = compose(ex5, ev5, d["judgments"], scores)
        report["v5"][arm] = {"verdicts": dict(collections.Counter(j["result"]["decision"] for j in d["judgments"])),
                             "incidents": len(built["composition"]["incidents"]),
                             "matrices": len(built["composition"]["matrices"]),
                             "eu_diesel_reasons": eu_reasons(d["judgments"]),
                             "score": score(V5_MAP, d["judgments"], built["composition"], built["assembly"]["groups"])}
    json.dump(report, open(out_path, "w"), ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:6000])


if __name__ == "__main__":
    main(*sys.argv[1:6])
