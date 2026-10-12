import unittest
from ingestion.topic_discovery_diagnostics import diagnose

class DiscoveryDiagnosticsTests(unittest.TestCase):
    def test_reports_seed_delta_and_uncertainty(self):
        result={"topic":"test","posts":11,"seed_posts":8,
                "queries":["test"],"expansion":[{"term":"observed"}],
                "document_expansion":[{"term":"example"}],
                "documents":[{"url":"https://example.com/a","distinct_accounts_observed":2}],
                "event_candidates":[{"document_count":1}],
                "errors":[]}
        d=diagnose(result)
        self.assertEqual(d["additional_posts"],3)
        self.assertEqual(d["query_terms_requested"],3)
        self.assertEqual(d["urls_with_two_or_more_observed_accounts"],1)
        self.assertTrue(any("drift" in x for x in d["limitations"]))
if __name__=="__main__":
    unittest.main()
