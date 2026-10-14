import unittest
from ingestion.nli_relation_audit import audit

def sample(a,b,overlap=.5):
 return {"edges":[{"url_a":"https://a.example/1","url_b":"https://b.example/2",
  "comparisons":[{"statement_a":{"text":"Statement A"},"statement_b":{"text":"Statement B"},
   "lexical_overlap":overlap,"directional_nli":{"a_to_b":{"label":a,"score":.9},
   "b_to_a":{"label":b,"score":.8}}}]}]}
class AuditTests(unittest.TestCase):
 def test_asymmetric_contradiction_requires_review(self):
  d=audit(sample("contradiction","neutral"))
  self.assertIn("asymmetric_contradiction",d["review_queue"][0]["flags"])
  self.assertIsNone(d["coverage"]["precision"])
 def test_high_overlap_neutral(self):
  d=audit(sample("neutral","neutral"))
  self.assertIn("high_overlap_both_neutral",d["review_queue"][0]["flags"])
 def test_low_overlap_neutral_not_flagged(self):
  d=audit(sample("neutral","neutral",.1))
  self.assertEqual(d["coverage"]["flagged_pairs"],0)
if __name__=="__main__":unittest.main()
