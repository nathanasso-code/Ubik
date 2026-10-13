import unittest
from ingestion.semantic_empirical_audit import audit
class SemanticAuditTests(unittest.TestCase):
    def test_deterministic_and_not_a_fake_precision_metric(self):
        report={"pairs":[{"similarity":.8,"left":{"url":f"https://a.example/{i}","title":"A"},
                          "right":{"url":f"https://b.example/{i}","title":"B"}} for i in range(100)]}
        a=audit(report,seed=42,sample_size=15);b=audit(report,seed=42,sample_size=15)
        self.assertEqual(a,b)
        self.assertEqual(len(a["items"]),15)
        self.assertIsNone(a["precision_estimate"])
        self.assertIsNone(a["recall_estimate"])
        self.assertEqual(len({x["frozen_rank"] for x in a["items"]}),15)
if __name__=="__main__":unittest.main()
