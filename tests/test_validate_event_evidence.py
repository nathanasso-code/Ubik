import unittest
from scripts.validate_event_evidence import validate


class EvidenceValidationTests(unittest.TestCase):
    def test_verified_pair_requires_document_evidence(self):
        reference = {"documents": [
            {"id": "a", "url": "https://a.example/1", "title": "A", "publisher": "A", "date": "2024-01-01", "evidence": "Release A"},
            {"id": "b", "url": "https://b.example/2", "title": "B", "publisher": "B", "date": "2024-01-01"},
        ], "pairs": [{"left": "a", "right": "b", "label": "same_event",
                      "review_status": "verified", "basis": "Same announcement"}]}
        result = validate(reference)
        self.assertFalse(result["valid_structure"])
        self.assertIn("missing_document_evidence", [x["kind"] for x in result["issues"]])

    def test_complete_pair_passes_structure_only(self):
        documents = [{"id": x, "url": "https://example.org/" + x, "title": x,
                      "publisher": x, "date": "2024-01-01", "evidence": "Evidence"}
                     for x in ("a", "b")]
        result = validate({"documents": documents, "pairs": [
            {"left": "a", "right": "b", "label": "different_event",
             "review_status": "verified", "basis": "Different announcements"}]})
        self.assertTrue(result["valid_structure"])

    def test_duplicate_pair_rejected(self):
        reference = {"documents": [{"id": x, "url": "https://example.org/" + x,
                     "title": x, "publisher": x} for x in ("a", "b")],
                     "pairs": [{"left": "a", "right": "b"}, {"left": "b", "right": "a"}]}
        self.assertFalse(validate(reference)["valid_structure"])


if __name__ == "__main__":
    unittest.main()
