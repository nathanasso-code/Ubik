import unittest
from scripts.build_epistemic_review_queue import build_queue


class EpistemicReviewQueueTests(unittest.TestCase):
    def test_balanced_unlabeled_deterministic(self):
        items = [
            {"id": f"a{i}", "source_id": "a", "url": f"https://a.example/{i}", "title": f"Event {i}"}
            for i in range(6)
        ] + [
            {"id": f"b{i}", "source_id": "b", "url": f"https://b.example/{i}", "title": f"Study {i}"}
            for i in range(6)
        ]
        result = build_queue({"items": items}, per_source=3, max_total=4)
        self.assertEqual(result["coverage"]["sampled_sources"], 2)
        self.assertEqual(result["coverage"]["sampled_observations"], 4)
        self.assertEqual([x["source_id"] for x in result["items"]], ["a", "b", "a", "b"])
        self.assertTrue(all(x["review_status"] == "unreviewed" and x["event_label"] is None for x in result["items"]))
        self.assertEqual(result, build_queue({"items": list(reversed(items))}, per_source=3, max_total=4))

    def test_duplicate_urls_and_missing_fields(self):
        data = {"items": [
            {"id": "a", "source_id": "one", "url": "https://x.example/1", "title": "News"},
            {"id": "b", "source_id": "one", "url": "https://x.example/1", "title": "News"},
            {"id": "c", "source_id": "two", "url": "https://x.example/1", "title": "Repost"},
            {"id": "d", "source_id": "two", "title": "No URL"},
        ]}
        result = build_queue(data)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(len({x["source_id"] for x in result["items"]}), 2)

    def test_invalid_limits(self):
        with self.assertRaises(ValueError):
            build_queue({}, per_source=0)
        with self.assertRaises(ValueError):
            build_queue({}, max_total=-1)


if __name__ == "__main__":
    unittest.main()
