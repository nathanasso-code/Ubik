"""Structural smoke fixture grounded in archived S473/S474 monarch card identities.
NOT an LLM extraction test: explicit relations are human-provided expectations.
Archive artifact: 12572749808, joint-results.json, A_qwen context 0 and B_deepseek context 0.
"""
import unittest
from ingestion.ubik_matrix_composer_v5 import compose_v5

class MonarchV5Structure(unittest.TestCase):
    def test_three_study_details_and_decline_outside(self):
        cards = [
            {"id": "study", "title": "Monarch migration tracking study", "kind": "container", "source_ids":["S473","S474"]},
            {"id": "tracking", "news_ids": ["n0","n3"], "source_ids": ["S473","S474"]},
            {"id": "routes", "news_ids": ["n1","n5"], "source_ids": ["S473","S474"]},
            {"id": "technology", "news_ids": ["n2","n6"], "source_ids": ["S473","S474"]},
            {"id": "decline", "news_ids": ["n4"], "source_ids": ["S473"],"context_signal":"background"},
        ]
        rels = [{"type":"part_of","source":child,"target":"study",
                 "evidence_status":"expected_not_model_extracted"}
                for child in ("tracking","routes","technology")]
        out = compose_v5(cards, rels)
        study = next(m for m in out["matrices"] if m["anchor_card"] == "study")
        self.assertEqual(set(study["cards"]), {"study","tracking","routes","technology"})
        self.assertEqual(out["memberships"]["decline"], ["decline"])
        self.assertEqual(len(study["part_of"]), 3)
        self.assertEqual(len(out["matrices"]),1)
        self.assertIn("decline", [g["anchor_card"] for g in out["single_source_groups"]])
        self.assertEqual(out["new_llm_calls"], 0)
    def test_ukraine_single_source_fragments_are_not_matrices(self):
        cards=[{"id":"executive_order","source_ids":["S1","S2","S3","S4"]},
               {"id":"diesel_agreement","source_ids":["S1","S2","S3","S4","S5","S6"]},
               {"id":"truce_fragment","source_ids":["S1"]},
               {"id":"refinery_attacks","source_ids":["S2"]},
               {"id":"n23_fragment","source_ids":["S3"]},
               {"id":"n30_fragment","source_ids":["S4"]}]
        out=compose_v5(cards,[])
        self.assertEqual({m["anchor_card"] for m in out["matrices"]},{"executive_order","diesel_agreement"})
        self.assertEqual(len(out["single_source_groups"]),4)

    def test_reaction_position_preserved(self):
        cards=[{"id":"study"},{"id":"reaction"}]
        rels=[{"type":"reacts_to","source":"reaction","target":"study","position":"criticism"}]
        out=compose_v5(cards,rels)
        self.assertEqual(out["reactions"][0]["position"],"criticism")
    def test_part_of_cycle_rejected(self):
        with self.assertRaises(ValueError):
            compose_v5([{"id":"a"},{"id":"b"}],
                       [{"type":"part_of","source":"a","target":"b"},
                        {"type":"part_of","source":"b","target":"a"}])

if __name__ == "__main__":
    unittest.main()
