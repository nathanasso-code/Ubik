import unittest
from ingestion.claim_representation import extract_sentence,from_adequacy
class ClaimSchemaTests(unittest.TestCase):
 def test_grounded_with_abstention(self):
  x=extract_sentence('The study showed a 23% reduction in symptoms among 450 patients.',
   url='https://example.org/a',source_id='example',kind='abstract',idx=1,level='A')
  self.assertEqual(x['predicate_candidate'],'finding')
  self.assertIsNone(x['subject'])
  self.assertEqual(x['quantities'][0]['value'],'23')
  self.assertEqual(x['status'],'structured_candidate_unverified')
 def test_no_relation_abstains(self):
  self.assertIsNone(extract_sentence('This is a general discussion about treatment and clinical care.',
   url='https://example.org/a',source_id='example',kind='abstract',idx=1,level='A'))
 def test_provenance_and_counts(self):
  d={'documents':[{'url':'https://example.org/a','source_id':'a','adequacy':{'level':'A','kind':'abstract',
   'claim_candidates':[{'sentence_index':0,'evidence_excerpt':'The study showed a 23% reduction in symptoms among 450 patients.'}]}}]}
  r=from_adequacy(d)
  self.assertEqual(r['coverage']['claim_candidates'],1)
  self.assertEqual(r['coverage']['verified_claims'],0)
 def test_negation_not_contradiction(self):
  x=extract_sentence('The study did not show a reduction in symptoms among patients.',
   url='https://example.org/a',source_id='a',kind='abstract',idx=0,level='A')
  self.assertEqual(x['polarity'],'negative_marker_present')
if __name__=='__main__':unittest.main()
