import unittest
from scripts.build_cross_event_review import negative_candidates


class CrossEventReviewTests(unittest.TestCase):
    def test_cross_family_pairs_are_not_verified(self):
        ref = {"documents": [
            {"id": "a", "url": "https://a.example", "event_family": "launch-one"},
            {"id": "b", "url": "https://b.example", "event_family": "launch-one"},
            {"id": "c", "url": "https://c.example", "event_family": "launch-two"},
        ]}
        result = negative_candidates(ref)
        self.assertEqual(result["coverage"]["total"], 2)
        self.assertEqual(result["candidates"][0]["review_status"], "unreviewed")
        self.assertFalse(result["candidates"][0]["verified"])

    def test_unassigned_family_does_not_create_negative(self):
        self.assertEqual(negative_candidates({"documents": [{"id": "a"}, {"id": "b"}]})["candidates"], [])

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            negative_candidates({}, 0)


if __name__ == "__main__":
    unittest.main()
