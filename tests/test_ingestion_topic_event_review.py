import unittest
from ingestion.topic_event_review import suggest


class TopicEventReviewTests(unittest.TestCase):
    def test_only_distinct_source_documents_can_be_nominated(self):
        base = {"topic": {"id": "ai-models"}, "visible": [
            {"url": "https://a.test/1", "title": "OpenAI launches Orion reasoning benchmark today",
             "source_ids": ["a"], "publisher": "A"},
            {"url": "https://b.test/1", "title": "OpenAI launches Orion reasoning benchmark worldwide",
             "source_ids": ["b"], "publisher": "B"},
            {"url": "https://a.test/2", "title": "OpenAI launches Orion reasoning benchmark updated",
             "source_ids": ["a"], "publisher": "A"},
            {"url": "https://c.test/1", "title": "Quantum computing advances in Europe",
             "source_ids": ["c"], "publisher": "C"},
        ]}
        result = suggest(base)
        self.assertEqual(result["automatic_merges"], 0)
        self.assertTrue(result["review_pairs"])
        self.assertTrue(all(p["review_status"] == "unverified_same_event_candidate"
                            for p in result["review_pairs"]))
        self.assertTrue(all(p["left"]["url"] != p["right"]["url"]
                            for p in result["review_pairs"]))
        self.assertFalse(any(p["left"]["publisher"] == p["right"]["publisher"]
                             for p in result["review_pairs"]))

    def test_event_matching_uses_full_pool_not_visible_cap(self):
        left = {"url": "https://a.test/x",
                "title": "Anthropic announces Orion reasoning benchmark results",
                "source_ids": ["a"]}
        right = {"url": "https://b.test/y",
                 "title": "Anthropic announces Orion reasoning benchmark findings",
                 "source_ids": ["b"]}
        report = {"visible": [left], "all_candidates": [left, right]}
        result = suggest(report)
        self.assertEqual(result["candidate_pool_size"], 2)
        self.assertEqual(result["candidate_pairs"], 1)

    def test_same_topic_not_sufficient(self):
        report = {"visible": [
            {"url": "https://a.test/1", "title": "OpenAI releases model Alpha",
             "source_ids": ["a"]},
            {"url": "https://b.test/2", "title": "OpenAI releases model Beta",
             "source_ids": ["b"]},
        ]}
        self.assertEqual(suggest(report)["candidate_pairs"], 0)


if __name__ == "__main__":
    unittest.main()
