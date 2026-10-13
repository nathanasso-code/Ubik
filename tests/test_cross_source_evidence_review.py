import unittest
from ingestion.cross_source_evidence_review import relate,compare
class RelationTests(unittest.TestCase):
 def test_unrelated(self):
  self.assertEqual(relate('climate temperature rainfall drought','surgery patient bone fracture')['relation'],'insufficient_overlap')
 def test_negation_flag_is_not_fact_check(self):
  a='The trial showed significant reduction in symptoms among patients'
  b='The trial showed no significant reduction in symptoms among patients'
  self.assertEqual(relate(a,b)['relation'],'possible_polarity_difference_review')
 def test_source_separation(self):
  d={'documents':[{'url':'https://a/1','source_id':'a','adequacy':{'level':'A','claim_candidates':[{'evidence_excerpt':'The trial showed significant reduction in symptoms among patients'}]}},
   {'url':'https://b/2','source_id':'b','adequacy':{'level':'A','claim_candidates':[{'evidence_excerpt':'The trial showed no significant reduction in symptoms among patients'}]}}]}
  self.assertEqual(compare(d)['coverage']['candidate_relations'],1)
if __name__=='__main__':unittest.main()
