import unittest
from scripts.baseline_verified_event_pairs import predict, tokens
from scripts.evaluate_verified_event_pairs import evaluate


class EventBaselineTests(unittest.TestCase):
    def test_distinct_titles_abstain_even_if_topically_related(self):
        ref = {"documents": [
            {"id": "a", "title": "OpenAI launches GPT-4o", "url": "https://a.example"},
            {"id": "b", "title": "OpenAI GPT-4o launches today", "url": "https://b.example"},
        ], "pairs": [{"left": "a", "right": "b", "label": "same_event", "review_status": "verified"}]}
        result = predict(ref)
        self.assertEqual(result["pairs"][0]["decision"], "abstain")
        self.assertEqual(evaluate(ref, result)["recall_including_abstentions_as_missed"], 0)

    def test_identical_titles_distinct_urls(self):
        ref = {"documents": [
            {"id": "a", "title": "Release XYZ", "url": "https://a.example"},
            {"id": "b", "title": "Release XYZ", "url": "https://b.example"},
        ], "pairs": [{"left": "a", "right": "b"}]}
        self.assertEqual(predict(ref)["pairs"][0]["decision"], "same_event")

    def test_tokenization(self):
        self.assertIn("gpt-4o", tokens("OpenAI launches GPT-4o"))


if __name__ == "__main__":
    unittest.main()
