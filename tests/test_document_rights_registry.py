import tempfile,unittest
from ingestion.document_rights_registry import rights
from ingestion.licensed_text_store import store_text
class RightsTests(unittest.TestCase):
 def test_unknown_wikinews_is_not_automatically_approved(self):
  p=rights('https://en.wikinews.org/wiki/Test')
  self.assertTrue(p['candidate_for_license_review'])
  self.assertFalse(p['store_full_text'])
 def test_arxiv_default_does_not_grant_republication(self):
  p=rights('https://arxiv.org/abs/1234.5678',license_id='ARXIV',verified=True,
   license_evidence_url='https://arxiv.org/licenses/nonexclusive-distrib/1.0/')
  self.assertFalse(p['display_full_text'])
 def test_verified_cc_by_can_be_stored(self):
  url='https://en.wikinews.org/wiki/Example'
  p=rights(url,license_id='CC-BY-4.0',verified=True,
    license_evidence_url='https://en.wikinews.org/wiki/Wikinews:Copyright')
  with tempfile.TemporaryDirectory() as directory:
   result=store_text(url,'Licensed example',p,directory=directory)
   self.assertTrue(result['stored'])
 def test_unknown_cannot_be_stored(self):
  with tempfile.TemporaryDirectory() as directory:
   with self.assertRaises(PermissionError):
    store_text('https://example.org/article','Article',rights('https://example.org/article'),directory=directory)
if __name__=='__main__':unittest.main()
