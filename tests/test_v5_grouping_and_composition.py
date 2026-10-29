"""Behaviour tests for cautious grouping, part_of validation and composition (no model calls).

Some tests pin down known limitations on purpose; they are marked LIMITATION and must be updated
deliberately if the behaviour is changed.
"""
import unittest

from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_monarch_v5_rejudge_core import cautious_groups
from ingestion.ubik_part_of_validator_v5 import resolve_part_of


def j(a, b, decision, direction=None):
    return {"left": a, "right": b, "result": {"decision": decision, "direction": direction}}


def card(cid, *sources):
    return {"id": cid, "events": [cid], "source_ids": list(sources)}


class CautiousGroups(unittest.TestCase):
    def events(self, *ids):
        return {i: {} for i in ids}

    def test_simple_equivalence_merges(self):
        g = cautious_groups(self.events("S1:a", "S2:a"), [j("S1:a", "S2:a", "equivalent")], {("S1:a", "S2:a"): 0.9})
        self.assertIn(["S1:a", "S2:a"], g["groups"])

    def test_distinct_is_a_permanent_veto(self):
        ev = self.events("S1:a", "S2:a", "S3:a")
        js = [j("S1:a", "S2:a", "equivalent"), j("S2:a", "S3:a", "equivalent"), j("S1:a", "S3:a", "distinct")]
        sc = {("S1:a", "S2:a"): 0.9, ("S2:a", "S3:a"): 0.8, ("S1:a", "S3:a"): 0.7}
        g = cautious_groups(ev, js, sc)
        self.assertNotIn(["S1:a", "S2:a", "S3:a"], g["groups"])
        self.assertTrue(any(c["reason"] == "permanent_distinct_veto" for c in g["conflicts"]))

    def test_one_event_per_source_in_a_card(self):
        ev = self.events("S1:a", "S1:b", "S2:a")
        js = [j("S1:a", "S2:a", "equivalent"), j("S1:b", "S2:a", "equivalent")]
        g = cautious_groups(ev, js, {("S1:a", "S2:a"): 0.9, ("S1:b", "S2:a"): 0.8})
        self.assertTrue(any(c["reason"] == "duplicate_source" for c in g["conflicts"]))

    def test_uncertain_creates_no_link(self):
        g = cautious_groups(self.events("S1:a", "S2:a"), [j("S1:a", "S2:a", "uncertain")], {("S1:a", "S2:a"): 0.9})
        self.assertEqual(g["groups"], [["S1:a"], ["S2:a"]])

    def test_LIMITATION_order_dependence_with_partial_comparisons(self):
        # a-b and a-c are equivalent, b-c never compared (not among candidates).
        # Whichever pair is processed first wins; the third event needs two confirmations and is left out.
        ev = self.events("S1:a", "S2:b", "S3:c")
        js = [j("S1:a", "S2:b", "equivalent"), j("S1:a", "S3:c", "equivalent")]
        g1 = cautious_groups(ev, js, {("S1:a", "S2:b"): 0.9, ("S1:a", "S3:c"): 0.8})
        g2 = cautious_groups(ev, js, {("S1:a", "S2:b"): 0.8, ("S1:a", "S3:c"): 0.9})
        self.assertIn(["S1:a", "S2:b"], g1["groups"])
        self.assertIn(["S1:a", "S3:c"], g2["groups"])


class PartOfValidation(unittest.TestCase):
    def test_cycle_is_quarantined(self):
        rels = [{"type": "part_of", "source": "x", "target": "y"}, {"type": "part_of", "source": "y", "target": "x"}]
        accepted, rejected = resolve_part_of(rels)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(rejected[0]["reason"], "self_or_cycle")


class Composition(unittest.TestCase):
    def test_reaction_attaches_to_its_target(self):
        out = compose_connected_v5([card("c:a", "S1", "S2"), card("c:r", "S3")],
                                   [{"type": "reacts_to", "source": "c:r", "target": "c:a"}])
        self.assertEqual(len(out["incidents"]), 1)
        self.assertEqual(out["incidents"][0]["presentation"], "matrix")

    def test_multi_target_reaction_does_not_bridge(self):
        out = compose_connected_v5([card("c:a", "S1"), card("c:b", "S2"), card("c:r", "S3")],
                                   [{"type": "reacts_to", "source": "c:r", "target": "c:a"},
                                    {"type": "reacts_to", "source": "c:r", "target": "c:b"}])
        self.assertEqual(len(out["incidents"]), 2)
        self.assertEqual(out["memberships"]["c:r"], ["incident:c:a", "incident:c:b"])

    def test_reactions_from_other_sources_do_not_make_a_matrix(self):
        out = compose_connected_v5([card("c:a", "S1"), card("c:r", "S2")],
                                   [{"type": "reacts_to", "source": "c:r", "target": "c:a"}])
        self.assertEqual(out["incidents"][0]["presentation"], "single_source")

    def test_isolated_card_stays_in_topic(self):
        out = compose_connected_v5([card("c:a", "S1")], [])
        self.assertEqual(out["topic_cards"], ["c:a"])

    def test_without_origins_sources_count_as_origins(self):
        # Unchanged v5/v5.1 behaviour when cards carry no independent_origin_ids.
        out = compose_connected_v5([card("c:a", "S1", "S2"), card("c:p", "S1")],
                                   [{"type": "part_of", "source": "c:p", "target": "c:a"}])
        self.assertEqual(out["incidents"][0]["presentation"], "matrix")
        self.assertEqual(out["incidents"][0]["origin_verification"], "provisional")

    def test_same_origin_feeds_do_not_corroborate(self):
        # v5.2: an outlet's article and its own social post are one origin, so no matrix.
        a = dict(card("c:a", "site", "masto"), independent_origin_ids=["outlet"])
        p = dict(card("c:p", "site"), independent_origin_ids=["outlet"])
        out = compose_connected_v5([a, p], [{"type": "part_of", "source": "c:p", "target": "c:a"}])
        self.assertEqual(out["incidents"][0]["presentation"], "single_source")
        self.assertEqual(out["incidents"][0]["origin_verification"], "registry")

    def test_two_origins_still_make_a_matrix(self):
        a = dict(card("c:a", "site", "other"), independent_origin_ids=["outlet", "other"])
        p = dict(card("c:p", "site"), independent_origin_ids=["outlet"])
        out = compose_connected_v5([a, p], [{"type": "part_of", "source": "c:p", "target": "c:a"}])
        self.assertEqual(out["incidents"][0]["presentation"], "matrix")

    def test_LIMITATION_reaction_from_a_structural_card_is_dropped(self):
        # A card that is part of a part_of component and also reacts to another component:
        # the reaction is neither attached nor kept in any incident.
        out = compose_connected_v5([card("c:a", "S1"), card("c:b", "S1"), card("c:t", "S2", "S3")],
                                   [{"type": "part_of", "source": "c:b", "target": "c:a"},
                                    {"type": "reacts_to", "source": "c:b", "target": "c:t"}])
        kept = [r for inc in out["incidents"] for r in inc["reactions"]]
        self.assertEqual(kept, [])


if __name__ == "__main__":
    unittest.main()
