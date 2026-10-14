import unittest
from ingestion.blinded_nli_annotation_packet import packet
class PacketTests(unittest.TestCase):
 def test_blinding_and_separate_gold_fields(self):
  d=packet({"review_queue":[{"url_a":"https://a","url_b":"https://b","statement_index":0,
   "text_a":"First claim","text_b":"Second claim","labels":["contradiction","contradiction"],
   "scores":[.99,.99],"flags":["symmetric_contradiction_review"]}]})
  item=d["items"][0]
  self.assertNotIn("labels",item)
  self.assertNotIn("scores",item)
  self.assertNotIn("flags",item)
  self.assertIsNone(item["event_identity_gold"])
  self.assertIsNone(item["statement_relation_gold"])
  self.assertEqual(d["coverage"]["annotated"],0)
if __name__=="__main__":unittest.main()
