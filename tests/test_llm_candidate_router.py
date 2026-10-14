import unittest
from ingestion.llm_candidate_router import route
class RouterTests(unittest.TestCase):
 def test_budget_and_priority(self):
  pairs=[{"url_a":"a","url_b":"b","title_a":"a","title_b":"b","semantic_similarity":.91,
    "title_jaccard":.1,"decision":"related_topic_or_unresolved"},
   {"url_a":"c","url_b":"d","semantic_similarity":.90,"title_jaccard":.5,
    "decision":"same_event_review_candidate"}]
  out=route({"pairs":pairs},1)
  self.assertEqual(out["coverage"]["queued_pairs"],1)
  self.assertEqual(out["queue"][0]["url_a"],"a")
  self.assertEqual(out["queue"][0]["status"],"queued_not_analyzed")
 def test_no_api_call_and_zero_budget(self):
  self.assertEqual(route({"pairs":[{"url_a":"a","url_b":"b","semantic_similarity":.99}]},0)["queue"],[])
 def test_reject_low_similarity(self):
  self.assertEqual(route({"pairs":[{"url_a":"a","url_b":"b","semantic_similarity":.2}]},30)["queue"],[])
if __name__=="__main__":unittest.main()
