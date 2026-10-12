import unittest
from ingestion.blind_relation_hypotheses import discover

class BlindRelationTests(unittest.TestCase):
    def test_discovers_unseeded_cross_publisher_co_mentions(self):
        rows=[{"url":"https://a.example/1","title":"Cloud infrastructure energy consumption increases"},
              {"url":"https://b.example/2","title":"Energy consumption and cloud infrastructure pressures"},
              {"url":"https://a.example/3","title":"Other unrelated news item"}]
        r=discover({"items":rows})
        self.assertEqual(r["query_seed_terms"],[])
        self.assertTrue(any(x["terms"]==["cloud","infrastructure"] for x in r["edges"]))
        self.assertTrue(all(x["relation_type"]=="undetermined" for x in r["edges"]))
        self.assertFalse(r["automatic_topic_creation"])
    def test_reposts_from_same_host_do_not_suffice(self):
        rows=[{"url":f"https://a.example/{i}","title":"Cloud infrastructure energy consumption"}
              for i in range(4)]
        self.assertEqual(discover({"items":rows})["edges"],[])
    def test_no_fabricated_relation_on_unrelated_titles(self):
        rows=[{"url":"https://a.example/1","title":"Solar electricity generation"},
              {"url":"https://b.example/2","title":"Regional election polling"}]
        self.assertEqual(discover({"items":rows})["edges"],[])
if __name__=="__main__":unittest.main()
