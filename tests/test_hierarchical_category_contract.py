import unittest
from ingestion.hierarchical_category_contract import validate_hierarchy
class CategoryTests(unittest.TestCase):
 def test_grounded_general_to_specific(self):
  text="The European Space Agency launched a new climate monitoring satellite."
  p={"levels":[{"label":"Science","evidence_quote":"Space Agency"},
   {"label":"Space","evidence_quote":"satellite"},
   {"label":"Earth observation","evidence_quote":"climate monitoring"}]}
  r=validate_hierarchy(p,text)
  self.assertTrue(r["accepted"]);self.assertEqual(r["depth"],3)
  self.assertFalse(r["automatically_published"])
 def test_hallucinated_specificity_rejected(self):
  p={"levels":[{"label":"Mars mining","evidence_quote":"mining on Mars"}]}
  self.assertEqual(validate_hierarchy(p,"A satellite launched.")["reason"],"ungrounded_category")
 def test_partial_hierarchy_allowed(self):
  p={"levels":[{"label":"Science","evidence_quote":"scientific"}]}
  self.assertTrue(validate_hierarchy(p,"A scientific report.")["accepted"])
if __name__=="__main__":unittest.main()
