import unittest
from scripts.audit_epistemic_pairs import audit


class PairAuditTests(unittest.TestCase):
    def test_diagnostics_do_not_infer_event_identity(self):
        data = {"items": [
            {"left_id": "a", "right_id": "b", "left_source": "one", "right_source": "two",
             "left_title": "Introduction to ML", "right_title": "Introduction to Deep ML",
             "similarity_hint": 0.8, "same_url": False},
            {"left_id": "a", "right_id": "c", "left_source": "one", "right_source": "three",
             "similarity_hint": 0.2, "same_url": False},
        ]}
        report = audit(data)
        self.assertEqual(report["pairs_above_threshold"], 1)
        self.assertEqual(report["selected_pairs"], 2)
        self.assertIsNone(report["review_priority"][0]["same_event_label"])
        self.assertEqual(report["review_priority"][0]["review_status"], "unreviewed")
        self.assertEqual(report["source_pair_distribution"][0]["count"], 1)

    def test_empty_and_bad_threshold(self):
        self.assertEqual(audit({})["pairs_above_threshold"], 0)
        with self.assertRaises(ValueError):
            audit({}, threshold=2)


if __name__ == "__main__":
    unittest.main()
