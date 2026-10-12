import unittest
from ingestion.global_discovery import global_candidates

class GlobalDiscoveryTests(unittest.TestCase):
    def test_cross_document_candidate_without_topic_seed(self):
        rows=[
          {"canonical_url_hint":"https://publisher-a.example/datacenter-attack",
           "title":"Datacenter infrastructure disrupted","connector":"rss","source_id":"feed-a"},
          {"canonical_url_hint":"https://publisher-b.example/infrastructure-report",
           "title":"New datacenter infrastructure report","connector":"rss","source_id":"feed-b"}]
        result=global_candidates({"observations":rows})
        self.assertIn("datacenter",[x["term"] for x in result["candidate_terms"]])
        self.assertFalse(result["topic_assignment_applied"])
        self.assertFalse(result["event_clustering_applied"])
    def test_duplicate_reposts_do_not_create_multiple_documents(self):
        rows=[{"canonical_url_hint":"https://publisher.example/one",
               "title":"Datacenter infrastructure","connector":"mastodon",
               "source_id":f"account-{i}"} for i in range(4)]
        result=global_candidates({"observations":rows})
        self.assertEqual(result["documents_observed"],1)
        self.assertEqual(result["candidate_terms"],[])
    def test_no_source_independence_claim(self):
        result=global_candidates({"observations":[]})
        self.assertTrue(any("independent" in x for x in result["limitations"]))
if __name__=="__main__":
    unittest.main()
