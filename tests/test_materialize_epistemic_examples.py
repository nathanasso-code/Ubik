import unittest
from scripts.materialize_epistemic_examples import materialize


class EventExampleTests(unittest.TestCase):
    def setUp(self):
        self.candidates = {"items": [{
            "left_url": "https://a.example/1", "right_url": "https://b.example/2",
            "left_title": "A release", "right_title": "B release",
            "left_source": "one", "right_source": "two", "similarity_hint": 0.75
        }]}

    def test_provenance_and_provisional_status(self):
        seed = {"dataset": "test", "entries": [{"candidate_index": 0, "label": "different_event",
            "rationale": "Different release", "review_status": "provisional", "full_text_verified": False}]}
        result = materialize(seed, self.candidates)
        self.assertEqual(result["summary"]["different_event"], 1)
        self.assertEqual(result["summary"]["gold_standard_eligible"], 0)
        self.assertEqual(result["entries"][0]["left"]["url"], "https://a.example/1")

    def test_uncertain_excluded_from_gold(self):
        seed = {"entries": [{"candidate_index": 0, "label": "uncertain"}]}
        self.assertEqual(materialize(seed, self.candidates)["summary"]["gold_standard_eligible"], 0)

    def test_invalid_or_duplicate_index(self):
        with self.assertRaises(ValueError):
            materialize({"entries": [{"candidate_index": 3, "label": "different_event"}]}, self.candidates)
        with self.assertRaises(ValueError):
            materialize({"entries": [{"candidate_index": 0, "label": "different_event"},
                                     {"candidate_index": 0, "label": "different_event"}]}, self.candidates)


if __name__ == "__main__":
    unittest.main()
