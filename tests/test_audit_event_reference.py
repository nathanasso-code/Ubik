import unittest
from scripts.audit_event_reference import audit


def ref(labels):
    return {"documents": [{"id": x, "url": "https://example.org/" + x, "title": x} for x in "abcd"],
            "pairs": [{"left": a, "right": b, "label": label, "review_status": "verified"}
                      for a, b, label in labels]}


class ReferenceAuditTests(unittest.TestCase):
    def test_positive_only_is_not_evaluation_ready(self):
        result = audit(ref([("a", "b", "same_event")]))
        self.assertFalse(result["held_out_evaluation_ready"])
        self.assertEqual(result["distinct_positive_event_components"], 1)

    def test_detects_transitive_contradiction(self):
        result = audit(ref([("a", "b", "same_event"), ("b", "c", "same_event"),
                            ("a", "c", "different_event")]))
        self.assertEqual(len(result["contradictions"]), 1)
        self.assertFalse(result["held_out_evaluation_ready"])

    def test_two_events_with_negative_can_meet_minimum(self):
        result = audit(ref([("a", "b", "same_event"), ("c", "d", "same_event"),
                            ("a", "c", "different_event")]))
        self.assertTrue(result["held_out_evaluation_ready"])

    def test_duplicate_document_url_rejected(self):
        data = ref([])
        data["documents"][1]["url"] = data["documents"][0]["url"]
        with self.assertRaises(ValueError):
            audit(data)

    def test_duplicate_pair_rejected(self):
        with self.assertRaises(ValueError):
            audit(ref([("a", "b", "same_event"), ("b", "a", "same_event")]))


if __name__ == "__main__":
    unittest.main()
