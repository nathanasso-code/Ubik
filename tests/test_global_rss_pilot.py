import json
import tempfile
import unittest
from pathlib import Path
from ingestion.global_rss_pilot import collect

class GlobalRSSPilotTests(unittest.TestCase):
    def test_no_topic_seed_and_bounded_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            reg=Path(directory)/"registry.json";out=Path(directory)/"out.json"
            reg.write_text(json.dumps({"purpose":"global_topic_agnostic_rss",
                "sources":[{"id":"world","name":"World Publisher","url":"https://example.org/rss","enabled":True,"kind":"rss"}]}))
            payload=b'<rss><channel><item><title>Regional infrastructure report</title><link>https://example.org/a</link></item></channel></rss>'
            result=collect(reg,out,lambda url:payload)
            self.assertEqual(result["coverage"]["observations"],1)
            self.assertEqual(result["items"][0]["topic_ids"],[])
            self.assertEqual(result["items"][0]["discovery_mode"],"global_unassigned")
    def test_rejects_oversized_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            reg=Path(directory)/"r.json";out=Path(directory)/"o.json"
            reg.write_text(json.dumps({"purpose":"global_topic_agnostic_rss",
                "sources":[{"id":str(i),"url":"https://example.org","kind":"rss","enabled":True} for i in range(3)]}))
            with self.assertRaises(ValueError):
                collect(reg,out,lambda _:b"",max_sources=2)
if __name__=="__main__":
    unittest.main()
