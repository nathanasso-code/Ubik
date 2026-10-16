import unittest
from ingestion.cross_source_pair_text_probe import run,select

class PairTextProbeTests(unittest.TestCase):
    def test_sample_and_deduplicate_urls(self):
        pairs=[]
        for i in range(80):
            pairs.append({"score":0.5,"left":{"url":"https://a.example/shared","title":"A","publisher":"A"},
                          "right":{"url":f"https://b.example/{i}","title":"B","publisher":"B"}})
        chosen=select({"top_pairs":pairs})
        self.assertEqual(len(chosen),24)
        calls=[]
        def fake(url):
            calls.append(url)
            return {"status":"get_success","alternative_extractors":{"trafilatura":{"substantial_800":True,"substantial_1200_180":True,"chars":2000,"words":350}}}
        result=run({"top_pairs":pairs},checker=fake)
        self.assertEqual(result["summary"]["unique_urls_attempted"],25)
        self.assertEqual(len(calls),25)
        self.assertEqual(result["summary"]["pairs_both_800_100"],24)
    def test_inaccessible_side_not_usable(self):
        pair={"score":0.9,"left":{"url":"https://a.example/a","title":"A","publisher":"A"},
              "right":{"url":"https://b.example/b","title":"B","publisher":"B"}}
        def fake(url):
            if "a.example" in url:return {"status":"get_failed"}
            return {"status":"get_success","alternative_extractors":{"trafilatura":{"substantial_800":True}}}
        result=run({"top_pairs":[pair]},checker=fake)
        self.assertEqual(result["summary"]["pairs_both_800_100"],0)
if __name__=="__main__":unittest.main()
