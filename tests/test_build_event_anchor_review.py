import unittest
from scripts.build_event_anchor_review import review_tasks


class EventAnchorReviewTests(unittest.TestCase):
    def test_multiple_feeds_and_no_automatic_labels(self):
        discovery = {"items": [
            {"id": "1", "source_id": "a", "title": "Meta Llama 3 release", "url": "https://a.example"},
            {"id": "2", "source_id": "b", "title": "Llama 3 release notes", "url": "https://b.example"},
            {"id": "3", "source_id": "a", "title": "Meta Llama 3 release update", "url": "https://c.example"},
        ]}
        result = review_tasks(discovery, [{"id": "llama", "query": "Llama 3 release", "product_aliases": ["llama 3"]}])
        items = result["anchors"][0]["candidate_observations"]
        self.assertEqual(len(items), 2)
        self.assertEqual(result["verified_event_pairs"], 0)
        self.assertTrue(all(x["event_label"] is None for x in items))

    def test_unrelated_numeric_versions_do_not_match(self):
        discovery = {"items": [
            {"id": "a", "source_id": "python", "title": "Python 2.7 and Python 3",
             "url": "https://example.org/python"},
            {"id": "b", "source_id": "news", "title": "Claude 3.7 Sonnet announced",
             "url": "https://example.org/claude"},
        ]}
        found = review_tasks(discovery, [{"id": "claude", "query": "Anthropic Claude 3.7 Sonnet launch", "product_aliases": ["claude 3.7"]}])
        self.assertEqual([x["observation_id"] for x in found["anchors"][0]["candidate_observations"]], ["b"])

    def test_empty(self):
        self.assertEqual(review_tasks({}, [{"id": "x", "query": "No matching", "product_aliases": ["no matching"]}])["anchors"][0]["candidate_observations"], [])

    def test_other_product_same_version_excluded(self):
        discovery = {"items": [
            {"id": "a", "source_id": "google", "title": "Gemini 3.7 Flash",
             "url": "https://example.org/gemini"},
            {"id": "b", "source_id": "anthropic", "title": "Claude 3.7 Sonnet",
             "url": "https://example.org/claude"},
        ]}
        result = review_tasks(discovery, [{"id": "claude", "query": "Claude 3.7",
                                           "product_aliases": ["claude 3.7"]}])
        self.assertEqual([x["observation_id"] for x in result["anchors"][0]["candidate_observations"]], ["b"])

    def test_missing_aliases_rejected(self):
        with self.assertRaises(ValueError):
            review_tasks({}, [{"id": "x", "query": "Claude 3.7"}])

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            review_tasks({}, [], 0)


if __name__ == "__main__":
    unittest.main()
