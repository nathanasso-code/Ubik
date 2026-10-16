import unittest
from ingestion.live_get_text_probe import select_urls,probe

class SamplingTests(unittest.TestCase):
    def setUp(self):
        self.snapshot={"items":[{"url":f"https://{host}.example.org/{i}","source_id":host} for host in ("a","b","c") for i in range(12)]}
    def test_seed_reproducible_and_balanced(self):
        a=select_urls(self.snapshot,max_urls=9,per_host=3,seed=23)
        b=select_urls(self.snapshot,max_urls=9,per_host=3,seed=23)
        self.assertEqual(a,b)
        self.assertEqual({host:sum(host+".example.org" in x["url"] for x in a) for host in ("a","b","c")},{"a":3,"b":3,"c":3})
        self.assertNotEqual(a,select_urls(self.snapshot,max_urls=9,per_host=3,seed=24))
    def test_no_network_and_metadata(self):
        out=probe(self.snapshot,max_urls=6,per_host=2,checker=lambda u:{"status":"get_success","content_tier":"long_abstract_metadata"})
        self.assertEqual(out["coverage"]["tested_urls"],6)
        self.assertEqual(out["sampling"]["method"],"stratified")
    def test_invalid_budget(self):
        with self.assertRaises(ValueError):
            select_urls(self.snapshot,max_urls=0)

if __name__=="__main__":
    unittest.main()
