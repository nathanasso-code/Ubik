import unittest
from ingestion.blind_semantic_neighbors import neighborhoods
class SemanticNeighborhoodTests(unittest.TestCase):
    def test_unseeded_cross_publisher_similarity(self):
        rows=[{"url":"https://a.example/a","title":"Electrical grid failure"},
              {"url":"https://b.example/b","title":"Rete elettrica in blackout"},
              {"url":"https://a.example/c","title":"A different local report"}]
        def embed(texts):
            self.assertTrue(all(x.startswith("query: ") for x in texts))
            return [[1,0],[.9,.1],[0,1]]
        r=neighborhoods({"items":rows},embed,min_similarity=.8)
        self.assertEqual(len(r["pairs"]),1)
        self.assertEqual(r["pairs"][0]["relation_type"],"undetermined")
        self.assertEqual(r["query_seed_terms"],[])
        self.assertFalse(r["automatic_topic_creation"])
    def test_same_host_not_independent(self):
        rows=[{"url":"https://a.example/1","title":"One"},
              {"url":"https://a.example/2","title":"Two"}]
        self.assertEqual(neighborhoods({"items":rows},lambda t:[[1,0],[1,0]])["pairs"],[])
    def test_deduplicates_url(self):
        rows=[{"url":"https://a.example/1","title":"One"}]*2
        r=neighborhoods({"items":rows},lambda t:[[1,0]])
        self.assertEqual(r["documents_examined"],1)
if __name__=="__main__":unittest.main()
