import unittest
from ingestion.empirical_france_refrigeration_case import build

class FrenchRefrigerationEvidenceTests(unittest.TestCase):
    def test_case_keeps_unverified_status_and_source_scopes(self):
        case=build()
        self.assertEqual(case["source_count"],3)
        self.assertEqual(len(case["observations"]),4)
        self.assertFalse(case["publication_approved"])
        self.assertFalse(case["truth_verified"])
        self.assertIsNone(case["independent_origin_count_verified"])
        self.assertEqual(case["full_article_texts_acquired_by_approved_fetcher"],0)
        claims={x["claim_key"] for x in case["observations"]}
        self.assertEqual(claims,{"intermarche_affected_stores","carrefour_affected_stores"})
    def test_quote_budget(self):
        case=build()
        self.assertTrue(all(len(x["evidence_excerpt"].split())<=25 for x in case["observations"]))

if __name__=="__main__":
    unittest.main()
