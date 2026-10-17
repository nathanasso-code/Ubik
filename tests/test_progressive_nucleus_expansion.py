import unittest
from ingestion.progressive_nucleus_expansion import expand

def pair(a,b,score=0.8):
    return {"score":score,"left":{"url":a,"publisher":a.split("/")[2],"title":a},
            "right":{"url":b,"publisher":b.split("/")[2],"title":b}}

class ProgressiveNucleusTests(unittest.TestCase):
    def test_multi_anchor_candidate(self):
        a,b,c="https://a.test/1","https://b.test/1","https://c.test/1"
        result=expand([pair(a,c),pair(b,c)], [a,b])
        self.assertEqual(result["candidate_count"],1)
        self.assertEqual(result["candidates"][0]["url"],c)
        self.assertEqual(result["candidates"][0]["support_count"],2)
    def test_single_anchor_not_enough(self):
        a,b,c="https://a.test/1","https://b.test/1","https://c.test/1"
        self.assertEqual(expand([pair(a,c)], [a,b])["candidate_count"],0)
    def test_no_transitive_chaining(self):
        a,b,c,d="https://a.test/1","https://b.test/1","https://c.test/1","https://d.test/1"
        self.assertEqual(expand([pair(a,c),pair(b,c),pair(c,d)], [a,b])["candidate_count"],1)
    def test_two_seeds_required(self):
        with self.assertRaises(ValueError):expand([],["https://a.test/1"])
if __name__=="__main__":unittest.main()
