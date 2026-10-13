import unittest
from ingestion.transparent_corpus_catalog import build

class CatalogTests(unittest.TestCase):
    def test_candidates_are_not_verified_or_published(self):
        rows={"items":[
          {"url":"https://a.example/1","title":"Event one","publisher":"A","description":"An event was reported with enough context for a publisher-supplied description. "+("Details. "*20)},
          {"url":"https://b.example/2","title":"Same event","publisher":"B","description":"Another outlet reports on the same topic, but this does not prove it is the same event. "+("Details. "*20)},
          {"url":"https://c.example/3","title":"Unrelated","publisher":"C","description":""}]}
        pairs={"pairs":[{"left":{"url":"https://a.example/1"},"right":{"url":"https://b.example/2"},"similarity":0.97}]}
        result=build(rows,pairs)
        self.assertEqual(result["coverage"]["candidate_multisource_groups"],1)
        self.assertEqual(result["coverage"]["single_original_sources"],1)
        self.assertEqual(result["coverage"]["full_bodies_acquired"],0)
        self.assertFalse(result["publication_approved"])
        self.assertFalse(result["multi_source_candidates"][0]["same_event_verified"])
        self.assertFalse(result["multi_source_candidates"][0]["claims_compared"])
    def test_duplicate_url_keeps_richer_description(self):
        x={"items":[{"url":"https://a.example/1","description":"a"},{"url":"https://a.example/1","description":"Long description with context. "*10}]}
        r=build(x)
        self.assertEqual(r["coverage"]["distinct_documents"],1)
        self.assertEqual(r["coverage"]["content_tiers"]["rss_extended_description"],1)
    def test_metadata_only_is_never_promoted(self):
        x={"items":[{"url":"https://a.example/1","description":""},{"url":"https://b.example/2","description":"Enough context. "*20}]}
        p={"pairs":[{"left":{"url":"https://a.example/1"},"right":{"url":"https://b.example/2"},"similarity":1.0}]}
        self.assertEqual(build(x,p)["coverage"]["candidate_multisource_groups"],0)

if __name__=="__main__":unittest.main()
