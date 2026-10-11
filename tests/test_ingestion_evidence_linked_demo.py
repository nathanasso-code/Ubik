import unittest
from ingestion.evidence_linked_demo import build

class EvidenceLinkedDemoTests(unittest.TestCase):
    def test_evidence_counts_are_observed_not_global(self):
        report=build()
        self.assertEqual(report["cards"][0]["id"],"anthropic-police-tip")
        self.assertEqual(report["cards"][0]["observed_reference_urls"],7)
        self.assertEqual(report["cards"][0]["reporting_origins"],7)
        self.assertEqual(next(c for c in report["cards"] if c["id"]=="ai-financing")["reporting_origins"],0)
        self.assertTrue(all(c["truth_score"] is None for c in report["cards"]))
        self.assertTrue(all(c["social_comments"]=="not_measured" for c in report["cards"]))
        self.assertTrue(report["not_exhaustive"])

if __name__=="__main__":
    unittest.main()
