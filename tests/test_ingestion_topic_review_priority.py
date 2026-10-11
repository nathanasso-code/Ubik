import unittest
from ingestion.topic_review_priority import build


class TopicReviewPriorityTests(unittest.TestCase):
    def test_all_candidates_preserved_and_pair_review_first(self):
        rows = [{"url": "https://a.test/x", "title": "A", "area_ids": ["research"],
                 "source_ids": ["a"], "published_raw": "2026-10-11"},
                {"url": "https://b.test/y", "title": "B", "area_ids": [],
                 "source_ids": ["b"], "published_raw": None}]
        topic = {"topic": {"id": "ai-models"}, "all_candidates": rows,
                 "visible": rows[:1]}
        evidence = {"items": [{"url": rows[0]["url"], "description_evidence": ["Source says something."]}]}
        pairs = {"review_pairs": [{"left": {"url": rows[0]["url"]},
                                   "right": {"url": rows[1]["url"]}}]}
        result = build(topic, evidence, pairs)
        self.assertEqual(result["documents_for_review"], 2)
        self.assertEqual(result["publication_approved"], 0)
        self.assertEqual(result["automatic_event_merges"], 0)
        self.assertEqual(result["items"][0]["review_reasons"][0], "possible_same_event_pair")
        self.assertIn("missing_substantive_description", result["items"][1]["review_reasons"])
        self.assertTrue(all(x["review_decision"] == "unreviewed" for x in result["items"]))

    def test_routine_evidence_not_called_verified(self):
        topic = {"all_candidates": [{"url": "https://a.test/1",
                                     "title": "A", "area_ids": ["research"],
                                     "published_raw": "2026-10-11"}]}
        evidence = {"items": [{"url": "https://a.test/1",
                               "description_evidence": ["A complete description."]}]}
        result = build(topic, evidence, {"review_pairs": []})
        self.assertEqual(result["items"][0]["review_reasons"], ["routine_content_review"])
        self.assertFalse(result["items"][0]["claim_verified"])


if __name__ == "__main__":
    unittest.main()
