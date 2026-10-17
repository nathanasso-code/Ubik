import unittest
from ingestion.concept_candidate_probe import candidate_pairs,concepts
class ConceptProbeTests(unittest.TestCase):
    def test_synonyms(self):
        self.assertIn("injury",concepts("journalist wounded"))
        self.assertIn("injury",concepts("photographer injured"))
    def test_generic_overlap_not_sufficient(self):
        rows=[{"url":"https://a.test/1","title":"Artificial intelligence research"},
              {"url":"https://b.test/2","title":"Artificial intelligence politics"}]
        self.assertEqual(candidate_pairs(rows,{"top_pairs":[]})["novel_candidate_pairs"],0)
    def test_novel_pair(self):
        rows=[{"url":"https://a.test/1","title":"Journalist wounded"},
              {"url":"https://b.test/2","title":"Photographer injured"}]
        result=candidate_pairs(rows,{"top_pairs":[]})
        self.assertEqual(result["novel_candidate_pairs"],1)
    def test_no_cross_domain_duplicates(self):
        rows=[{"url":"https://a.test/1","title":"Journalist wounded"},
              {"url":"https://a.test/2","title":"Photographer injured"}]
        self.assertEqual(candidate_pairs(rows,{"top_pairs":[]})["novel_candidate_pairs"],0)
    def test_excludes_baseline(self):
        rows=[{"url":"https://a.test/1","title":"Journalist wounded"},
              {"url":"https://b.test/2","title":"Photographer injured"}]
        base={"top_pairs":[{"left":{"url":rows[0]["url"]},"right":{"url":rows[1]["url"]}}]}
        self.assertEqual(candidate_pairs(rows,base)["novel_candidate_pairs"],0)
if __name__=="__main__":unittest.main()
