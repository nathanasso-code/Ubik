import unittest
from ingestion.semantic_relation_contract import validate_relation,json_schema
class ContractTests(unittest.TestCase):
 def setUp(self):
  self.sources={"a":"The company announced a new battery.","b":"The new battery will launch next year."}
  self.p={"document_a_id":"a","document_b_id":"b","event_relation":"related_development",
          "semantic_relation":"adds_detail","evidence":[{"document_id":"a","quote":"announced a new battery"},
            {"document_id":"b","quote":"will launch next year"}]}
 def test_grounded_relation(self):
  r=validate_relation(self.p,self.sources)
  self.assertTrue(r["accepted"]);self.assertFalse(r["asserts_factual_truth"])
  self.assertFalse(r["automatic_merge_allowed"])
 def test_unsupported_quote_abstains(self):
  self.p["evidence"][1]["quote"]="launches today"
  self.assertEqual(validate_relation(self.p,self.sources)["reason"],"ungrounded_quote")
 def test_missing_second_source_abstains(self):
  self.p["evidence"][1]["document_id"]="a"
  self.p["evidence"][1]["quote"]="The company announced a new battery."
  self.assertEqual(validate_relation(self.p,self.sources)["reason"],"missing_document_evidence")
 def test_schema_has_no_truth_verdict(self):
  self.assertNotIn("truth_verdict",json_schema()["properties"])
if __name__=="__main__":unittest.main()
