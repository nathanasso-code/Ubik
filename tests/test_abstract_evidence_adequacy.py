import unittest
from ingestion.abstract_evidence_adequacy import qualify,analyze
class AdequacyTests(unittest.TestCase):
 def test_informative_abstract(self):
  text=('We conducted a randomized study of 450 patients across six clinics. '
   'Results showed a 23 percent reduction in symptoms after twelve weeks. '
   'The findings suggest benefits, although limitations include a short follow-up period.')
  result=qualify(text,kind='abstract')
  self.assertEqual(result['level'],'A')
  self.assertTrue(result['claim_candidates'])
 def test_long_but_empty(self):
  text=' '.join(['A wonderful overview of the topic and all the latest news.']*25)
  self.assertEqual(qualify(text)['level'],'C')
 def test_short_teaser(self):
  self.assertEqual(qualify('Breaking news: major announcement expected today.')['level'],'C')
 def test_no_claims_for_inadequate(self):
  self.assertEqual(qualify('The results are interesting.')['claim_candidates'],[])
 def test_corpus_counts(self):
  out=analyze({'items':[{'url':'https://example.org/1','description':'Hello.'}]})
  self.assertEqual(out['coverage']['level_C'],1)
if __name__=='__main__':unittest.main()
