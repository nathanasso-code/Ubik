import unittest
from scripts.build_epistemic_pair_queue import candidate_pairs


class PairQueueTests(unittest.TestCase):
    def test_rank_and_keep_unverified(self):
        items = [
            {"observation_id": "a", "title": "Orion model released today", "url": "https://a.example/1", "source_id": "a"},
            {"observation_id": "b", "title": "Orion model released worldwide", "url": "https://b.example/2", "source_id": "b"},
            {"observation_id": "c", "title": "Neuroscience memory symposium", "url": "https://c.example/3", "source_id": "c"},
        ]
        output = candidate_pairs({"items": items})
        self.assertEqual(output["items"][0]["left_id"], "a")
        self.assertEqual(output["items"][0]["right_id"], "b")
        self.assertIsNone(output["items"][0]["same_event_label"])
        self.assertEqual(output["items"][0]["review_status"], "unreviewed")
        self.assertEqual(output, candidate_pairs({"items": list(reversed(items))}))

    def test_same_url_not_independent_event_confirmation(self):
        items = [
            {"observation_id": "a", "title": "Alpha", "url": "https://a.example/1"},
            {"observation_id": "b", "title": "Beta", "url": "https://a.example/1"},
        ]
        result = candidate_pairs({"items": items})
        self.assertEqual(result["items"][0]["reason"], "same_url")
        self.assertIsNone(result["items"][0]["same_event_label"])

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            candidate_pairs({"items": []}, 0)
        with self.assertRaises(ValueError):
            candidate_pairs({"items": [{"observation_id": "x"}, {"observation_id": "x"}]})


if __name__ == "__main__":
    unittest.main()
