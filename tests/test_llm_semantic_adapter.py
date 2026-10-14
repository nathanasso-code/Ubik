import unittest
from ingestion.llm_semantic_adapter import run,evaluate
class AdapterTests(unittest.TestCase):
 def test_dry_run_never_calls_api(self):
  q={"queue":[{"pair_id":"1","url_a":"u1","url_b":"u2"}]}
  docs=[{"url":"u1","title":"A","description":"A new satellite launched."},
        {"url":"u2","title":"B","description":"The satellite carries a camera."}]
  result=run(q,docs,execute=False)
  self.assertEqual(result["coverage"]["ready"],1)
  self.assertEqual(result["coverage"]["analyzed"],0)
 def test_evidence_and_categories(self):
  sources={"a":"A satellite launched.","b":"The satellite carries a camera."}
  proposal={"document_a_id":"a","document_b_id":"b","event_relation":"related_development",
   "semantic_relation":"adds_detail","evidence":[{"document_id":"a","quote":"satellite launched"},
     {"document_id":"b","quote":"satellite carries a camera"}],
   "category_a":{"levels":[{"label":"Space","evidence_quote":"satellite"}]},
   "category_b":{"levels":[{"label":"Space","evidence_quote":"satellite"}]}}
  result=evaluate(proposal,sources)
  self.assertTrue(result["accepted_for_review"])
  self.assertFalse(result["automatically_published"])
  proposal["category_b"]["levels"][0]["evidence_quote"]="invented quote"
  self.assertFalse(evaluate(proposal,sources)["accepted_for_review"])
if __name__=="__main__":unittest.main()
