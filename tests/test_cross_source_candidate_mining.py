import unittest
from ingestion.cross_source_candidate_mining import build

class CandidateMiningTests(unittest.TestCase):
    def test_cross_publisher_similar_pair_and_no_same_host(self):
        rows=[
            {"url":"https://a.example/1","title":"European leaders discuss Ukraine peace talks in Brussels","description":"Leaders gather in Brussels to discuss Ukraine peace talks","publisher":"A"},
            {"url":"https://b.example/2","title":"Ukraine peace talks discussed by European leaders in Brussels","description":"European leaders meet in Brussels for Ukraine peace talks","publisher":"B"},
            {"url":"https://a.example/3","title":"European leaders discuss Ukraine peace talks again","description":"Ukraine peace talks discussed in Brussels","publisher":"A"},
            {"url":"https://c.example/4","title":"Scientists discover new deep sea coral species","description":"Marine biology discovery in Pacific Ocean","publisher":"C"}]
        result=build(rows)
        self.assertEqual(result["documents"],4)
        self.assertTrue(result["top_pairs"])
        for p in result["top_pairs"]:
            from urllib.parse import urlsplit
            self.assertNotEqual(urlsplit(p["left"]["url"]).hostname,urlsplit(p["right"]["url"]).hostname)
        self.assertEqual(result["top_pairs"][0]["left"]["publisher"],"A")
        self.assertEqual(result["top_pairs"][0]["right"]["publisher"],"B")
    def test_duplicate_url_collapses(self):
        row={"url":"https://a.example/1","title":"Ukraine peace talks in Brussels","publisher":"A"}
        self.assertEqual(build([row,row])["documents"],1)
if __name__=="__main__":unittest.main()
