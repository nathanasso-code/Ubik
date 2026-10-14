import unittest
from ingestion.statement_relation_pilot import claims,compare
class StatementRelationTests(unittest.TestCase):
 def test_provenance(self):
  doc={"url":"https://example.org/a","title":"Court sentences defendant in murder trial","description":"The judge imposed a lengthy prison term after the trial.","source_id":"publisher"}
  out=claims(doc)
  self.assertEqual(out[0]["source_url"],doc["url"])
  self.assertEqual(out[0]["evidence_location"],"title")
 def test_directional_entailment_not_equivalence(self):
  items=[{"url":"https://example.org/a","title":"Court sentences defendant in murder trial"},
         {"url":"https://example.org/b","title":"Court sentences defendant to forty years in murder trial"}]
  pair={"url_a":items[0]["url"],"url_b":items[1]["url"],"decision":"same_event_review_candidate"}
  def predictor(x,y):
   return {"label":"entailment" if len(x)>len(y) else "neutral","score":.8}
  result=compare({"items":items},{"pairs":[pair]},predictor)
  self.assertEqual(result["coverage"]["nli_calls"],2)
  self.assertEqual(result["edges"][0]["comparisons"][0]["relation"],"model_directional_entailment_candidate")
 def test_no_model_does_not_invent_relation(self):
  items=[{"url":"https://example.org/a","title":"Minister denies proposed reform"},
         {"url":"https://example.org/b","title":"Minister confirms proposed reform"}]
  pair={"url_a":items[0]["url"],"url_b":items[1]["url"]}
  result=compare({"items":items},{"pairs":[pair]})
  self.assertEqual(result["edges"][0]["comparisons"][0]["relation"],"not_assessed")
if __name__=="__main__":unittest.main()
