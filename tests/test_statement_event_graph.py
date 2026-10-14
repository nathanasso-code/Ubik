import unittest
from ingestion.statement_event_graph import graph, classify_pair

class GraphTests(unittest.TestCase):
 def test_no_transitive_chain(self):
  urls=["https://a.test/x","https://b.test/x","https://c.test/x"]
  items=[{"url":u,"title":"Court sentences suspect in murder trial","source_id":u} for u in urls]
  pairs=[{"url_a":urls[i],"url_b":urls[j],"decision":"same_event_review_candidate"} for i,j in [(0,1),(1,2)]]
  result=graph({"items":items},{"pairs":pairs})
  self.assertEqual(result["coverage"]["complete_link_groups"],1)
  self.assertEqual(len(result["complete_link_review_groups"][0]["urls"]),2)
 def test_temporal_flag(self):
  a={"url":"https://a.test/x","title":"Pope will undergo surgery tomorrow"}
  b={"url":"https://b.test/x","title":"Pope underwent surgery yesterday"}
  result=classify_pair({"url_a":a["url"],"url_b":b["url"],"decision":"same_event_review_candidate"},{a["url"]:a,b["url"]:b})
  self.assertIn("temporal_modality_mismatch",result["flags"])
  self.assertEqual(result["review_status"],"unreviewed")

if __name__=="__main__":unittest.main()
