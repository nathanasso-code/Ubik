import unittest
from scripts.evaluate_verified_event_pairs import evaluate


class VerifiedEventEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.ref = {
            "documents": [{"id": x} for x in ("a", "b", "c")],
            "pairs": [
                {"left": "a", "right": "b", "label": "same_event", "review_status": "verified"},
                {"left": "a", "right": "c", "label": "different_event", "review_status": "verified"},
                {"left": "b", "right": "c", "label": "same_event", "review_status": "provisional"},
            ],
        }

    def test_abstention_is_not_correct_negative(self):
        result = evaluate(self.ref, {"pairs": [{"left": "a", "right": "b", "decision": "same_event"}]})
        self.assertEqual(result["verified_reference_pairs"], 2)
        self.assertEqual((result["tp"], result["abstained"]), (1, 1))
        self.assertEqual(result["precision_on_merges"], 1.0)

    def test_false_merge(self):
        result = evaluate(self.ref, {"pairs": [
            {"left": "a", "right": "b", "decision": "different_event"},
            {"left": "a", "right": "c", "decision": "same_event"},
        ]})
        self.assertEqual((result["fp"], result["fn"]), (1, 1))
        self.assertEqual(result["precision_on_merges"], 0.0)
        self.assertEqual(result["recall_including_abstentions_as_missed"], 0.0)

    def test_undefined_precision(self):
        self.assertIsNone(evaluate(self.ref, {"pairs": []})["precision_on_merges"])

    def test_reject_duplicate_predictions(self):
        with self.assertRaises(ValueError):
            evaluate(self.ref, {"pairs": [
                {"left": "a", "right": "b", "decision": "same_event"},
                {"left": "b", "right": "a", "decision": "same_event"},
            ]})


if __name__ == "__main__":
    unittest.main()
