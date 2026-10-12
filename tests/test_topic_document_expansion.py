import unittest
from ingestion.topic_document_expansion import propose_document_terms
from ingestion.topic_event_candidates import group_document_candidates

def record(account,url,post):
    return {"source_id":account,"url":post,"metadata":{"linked_documents":[url]}}

class DocumentDiscoveryTests(unittest.TestCase):
    def test_observed_terms_only_and_auditable(self):
        rows=[record("a","https://site.one/strikes-datacenter-infrastructure","https://post/1"),
              record("b","https://site.two/datacenter-infrastructure-disruption","https://post/2")]
        result=propose_document_terms(rows,["Ukraine"],min_accounts=2)
        self.assertTrue(any(x["term"]=="datacenter" for x in result))
        self.assertFalse(any(x["term"]=="yandex" for x in result))
        self.assertEqual(len(next(x for x in result if x["term"]=="datacenter")["supporting_posts"]),2)
    def test_no_single_author_promotion(self):
        rows=[record("a","https://one/a/datacenter-infrastructure","https://post/1"),
              record("a","https://two/b/datacenter-infrastructure","https://post/2")]
        self.assertEqual(propose_document_terms(rows),[])
    def test_event_grouping_is_explicitly_unverified(self):
        docs=[{"url":"https://one.com/strike-on-datacenter-infrastructure","post_urls":["https://p/1"]},
              {"url":"https://two.com/datacenter-infrastructure-strike","post_urls":["https://p/2"]}]
        groups=group_document_candidates(docs,threshold=.4)
        self.assertEqual(groups[0]["document_count"],2)
        self.assertEqual(groups[0]["status"],"candidate_unverified")
if __name__=="__main__":
    unittest.main()
