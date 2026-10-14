import unittest
from ingestion.evaluate_nli_gold import evaluate
class GoldEvaluationTests(unittest.TestCase):
 def setUp(self):
  self.audit={"review_queue":[{"url_a":"a","url_b":"b","statement_index":0,"labels":["entailment","neutral"]}]}
 def test_no_gold_no_accuracy(self):
  result=evaluate(self.audit,{"annotations":[]})
  self.assertIsNone(result["accuracy"])
 def test_directional_label(self):
  gold={"annotations":[{"url_a":"a","url_b":"b","statement_index":0,"label":"a_entails_b"}]}
  result=evaluate(self.audit,gold)
  self.assertEqual(result["accuracy"],1.0)
 def test_invalid_gold_rejected(self):
  with self.assertRaises(ValueError):
   evaluate(self.audit,{"annotations":[{"url_a":"a","url_b":"b","statement_index":0,"label":"verified_true"}]})
if __name__=="__main__":unittest.main()
