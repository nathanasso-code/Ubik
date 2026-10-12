import unittest
from ingestion.issue_candidates import propose_issues


class IssueCandidateTests(unittest.TestCase):
    def test_source_grounding_no_invented_summary(self):
        report = {"topic_id": "ai-models", "items": [
            {"url": "https://example.org/a", "title": "AI model evaluation questioned",
             "description_evidence": ["Original source reports a contested evaluation."]},
            {"url": "https://example.org/b", "title": "A new benchmark",
             "description_evidence": []},
        ]}
        result = propose_issues(report, limit=2)
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(result["items"][0]["sources"][0]["evidence_basis"], "feed_description_verbatim")
        for issue in result["items"]:
            self.assertIsNone(issue["card"]["summary"])
            self.assertEqual(issue["publication"], "blocked")
            self.assertTrue(issue["review_required"])
            self.assertEqual(issue["quality_flags"]["controversy"], "not_assessed")
            self.assertEqual(issue["claims"], [])

    def test_duplicate_url_and_invalid_url(self):
        rows = [{"url": "https://example.org/a", "title": "Test"},
                {"url": "https://example.org/a", "title": "Duplicate"},
                {"url": "javascript:alert(1)", "title": "Invalid"}]
        self.assertEqual(propose_issues({"topic_id": "ai", "items": rows})["candidate_count"], 1)

    def test_missing_topic_and_invalid_limit(self):
        with self.assertRaises(ValueError):
            propose_issues({"items": []})
        with self.assertRaises(ValueError):
            propose_issues({"topic_id": "ai", "items": []}, limit=0)


if __name__ == "__main__":
    unittest.main()
