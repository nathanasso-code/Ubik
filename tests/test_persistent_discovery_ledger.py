import unittest
from ingestion.persistent_discovery_ledger import merge,canonical
class LedgerTests(unittest.TestCase):
    def test_tracking_duplicate_and_provenance(self):
        rss={'items':[{'url':'https://www.example.org/news/a?utm_source=rss','title':'Example','source_id':'test'}]}
        hybrid={'documents':[{'url':'https://example.org/news/a','social_providers':['bluesky'],
           'social_post_urls':['https://bsky.app/profile/example/post/1'],
           'discovery_origins':['social_shared_url']}]}
        access={'probes':[{'url':'https://example.org/news/a','status':'get_success',
              'content_tier':'substantial_article_text_accessible','article_element_chars':3000}]}
        result=merge({},rss,hybrid,access,observed_at='2026-10-13T00:00:00Z')
        self.assertEqual(result['coverage']['distinct_urls'],1)
        d=result['documents'][0]
        self.assertEqual(d['social_providers'],['bluesky'])
        self.assertEqual(len(d['access_tests']),1)
        self.assertEqual(result['coverage']['with_substantial_article_text_evidence'],1)
        again=merge(result,rss,hybrid,access,observed_at='2026-10-14T00:00:00Z')
        self.assertEqual(len(again['documents'][0]['access_tests']),1)
    def test_reject_private_url_schemes_and_credentials(self):
        self.assertIsNone(canonical('file:///etc/passwd'))
        self.assertIsNone(canonical('https://user:password@example.org/a'))
    def test_old_documents_survive_new_snapshot(self):
        old={'documents':[{'url':'https://example.org/old','titles':['old'],'first_seen':'before'}]}
        result=merge(old,{'items':[]},{'documents':[]},{'probes':[]},observed_at='now')
        self.assertEqual(result['coverage']['distinct_urls'],1)
        self.assertEqual(result['documents'][0]['first_seen'],'before')
if __name__=='__main__':unittest.main()
