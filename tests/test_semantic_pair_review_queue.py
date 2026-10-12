import unittest
from ingestion.epistemic_review_queue import review_queue
class SemanticPairReviewQueueTests(unittest.TestCase):
    def test_preserves_frozen_ranks_and_no_publication(self):
        pairs=[{"similarity":1-i/100,"left":{"url":f"https://a.example/{i}","host":"a.example","title":f"A{i}"},
                "right":{"url":f"https://b.example/{i}","host":"b.example","title":f"B{i}"}} for i in range(10)]
        r=review_queue({"pairs":pairs},limit=6)
        self.assertEqual(len(r["selected"]),6)
        self.assertIn(1,[x["frozen_rank"] for x in r["selected"]])
        self.assertIn(10,[x["frozen_rank"] for x in r["selected"]])
        self.assertFalse(r["automatic_publication"])
        self.assertFalse(r["automatic_topic_creation"])
        self.assertTrue(all(x["epistemic_relation"]=="not_assessed" for x in r["selected"]))
if __name__=="__main__":unittest.main()
