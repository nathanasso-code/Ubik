import unittest
from datetime import datetime, timezone
from ingestion.topic_feed_pilot import select


class TopicFeedPilotTests(unittest.TestCase):
    def test_keeps_distinct_stories_and_balances_publishers(self):
        items = [
            {"url": f"https://a.test/{i}", "title": f"New GPT-{i} language model release",
             "source_id": "a", "publisher": "A", "published_raw": "2026-10-10T10:00:00Z"}
            for i in range(5)
        ] + [
            {"url": "https://b.test/1", "title": "Independent language model benchmark",
             "source_id": "b", "publisher": "B", "published_raw": "2026-10-10T10:00:00Z"},
            {"url": "https://c.test/1", "title": "Unrelated football match",
             "source_id": "c", "publisher": "C", "published_raw": "2026-10-10T10:00:00Z"},
        ]
        result = select({"items": items}, limit=3,
                        now=datetime(2026, 10, 11, tzinfo=timezone.utc))
        self.assertEqual(result["candidate_documents"], 6)
        self.assertEqual(len(result["visible"]), 3)
        self.assertIn("b", [x["source_ids"][0] for x in result["visible"]])
        self.assertTrue(all(x["display_kind"] == "standalone_source_candidate" for x in result["visible"]))
        self.assertFalse(result["automatic_publication"])

    def test_deduplicates_same_url_without_claiming_independence(self):
        item = {"url": "https://a.test/x", "title": "New LLM benchmark",
                "source_id": "a", "published_raw": "2026-10-10"}
        result = select({"items": [item, {**item, "source_id": "b"}]},
                        now=datetime(2026, 10, 11, tzinfo=timezone.utc))
        self.assertEqual(result["candidate_documents"], 1)
        self.assertEqual(result["visible"][0]["source_ids"], ["a", "b"])
        self.assertEqual(result["visible"][0]["same_event"], "unverified")

    def test_excludes_old_or_non_ai(self):
        items = [{"url": "https://a.test/old", "title": "GPT-4 language model",
                  "source_id": "a", "published_raw": "2024-01-01"}]
        result = select({"items": items}, now=datetime(2026, 10, 11, tzinfo=timezone.utc))
        self.assertEqual(result["candidate_documents"], 0)


if __name__ == "__main__":
    unittest.main()
