import unittest
from ingestion.curated_evidence_merge import assemble_case,categorize
from ingestion.empirical_mx_storms_case import build
class CuratedMergeTests(unittest.TestCase):
    def test_real_case_is_not_auto_verified(self):
        case=build()
        self.assertEqual(case["source_count"],4)
        self.assertEqual(len(case["potential_updates"]),1)
        self.assertEqual(case["semantic_category"]["category"],"Ambiente e clima")
        self.assertFalse(case["same_event_verified"])
        self.assertFalse(case["truth_verified"])
        self.assertFalse(case["publication_approved"])
        self.assertEqual(case["full_article_texts_acquired_by_approved_fetcher"],0)
    def test_different_event_rejected(self):
        case=build();obs=case["observations"]
        modified=[dict(obs[0]),dict(obs[1],event_key="other")]
        with self.assertRaises(ValueError):assemble_case(modified)
    def test_source_agency_reuse_not_independent(self):
        case=build()
        self.assertLessEqual(case["declared_origin_groups"],case["source_count"])\n        self.assertIsNone(case["independent_origin_count_verified"])
if __name__=="__main__":unittest.main()
