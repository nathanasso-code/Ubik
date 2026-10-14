import unittest
from ingestion.nli_publication_gate import gate
class GateTests(unittest.TestCase):
 def case(self,labels,flags=None):
  return gate({"review_queue":[{"url_a":"a","url_b":"b","statement_index":0,"labels":labels,"flags":flags or []}]})
 def test_symmetric_contradiction_never_asserted(self):
  d=self.case(["contradiction","contradiction"])
  self.assertEqual(d["decisions"][0]["decision"],"human_review_possible_contradiction")
  self.assertFalse(d["decisions"][0]["automatic_contradiction_claim_allowed"])
 def test_asymmetric_contradiction_abstains(self):
  d=self.case(["contradiction","neutral"],["asymmetric_contradiction"])
  self.assertEqual(d["decisions"][0]["decision"],"abstain_directional_conflict")
 def test_entailment_never_auto_merges(self):
  d=self.case(["entailment","entailment"])
  self.assertEqual(d["coverage"]["automatic_merges"],0)
if __name__=="__main__":unittest.main()
