import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("discovery", Path(__file__).resolve().parents[1] / "scripts/discover_ai_sources.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RSS = b"""<rss version="2.0"><channel><item><title>New model</title><link>https://example.org/a?utm_source=feed</link><guid>g1</guid><pubDate>Thu, 08 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>"""
ATOM = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Independent study</title><id>paper-1</id><link href="https://example.org/b" rel="alternate"/><updated>2026-10-08T11:00:00Z</updated></entry></feed>"""

class DiscoveryTests(unittest.TestCase):
    def test_rss_and_atom(self):
        source = {"id": "s", "name": "Publisher"}
        self.assertEqual(module.parse_feed(RSS, source)[0]["url"], "https://example.org/a")
        self.assertEqual(module.parse_feed(ATOM, source)[0]["title"], "Independent study")
        self.assertIsNone(module.canonical("javascript:alert(1)"))

    def test_attribution_and_provenance(self):
        rss = b'<rss xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><item><title>A</title><link>https://example.org/a</link><dc:creator>Researcher A</dc:creator></item></channel></rss>'
        item = module.parse_feed(rss, {"id":"x","name":"Publisher","url":"https://example.org/feed"})[0]
        self.assertEqual(item["authors"], ["Researcher A"])
        self.assertEqual(item["attribution_basis"], "entry")
        self.assertEqual(item["discovered_from"], "https://example.org/feed")
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><author><name>Researcher B</name></author><entry><title>B</title><link href="https://example.org/b"/><id>b</id></entry></feed>'
        item2 = module.parse_feed(atom, {"id":"x","name":"Publisher","url":"https://example.org/feed"})[0]
        self.assertEqual(item2["authors"], ["Researcher B"])
        self.assertEqual(item2["attribution_basis"], "feed")
        email = b'<rss><channel><item><title>C</title><link>https://example.org/c</link><author>private@example.org</author></item></channel></rss>'
        self.assertEqual(module.parse_feed(email, {"id":"x","name":"Publisher","url":"https://example.org/feed"})[0]["authors"], [])

    def test_repeat_and_failure_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, out = Path(tmp)/"registry.json", Path(tmp)/"result.json"
            reg.write_text(json.dumps({"topic_id": "ai-models", "sources": [
                {"id": "one", "name": "First", "url": "https://example.org/feed", "enabled": True, "kind": "rss"},
                {"id": "bad", "name": "Bad", "url": "https://example.org/fail", "enabled": True, "kind": "rss"}]}))
            def fetch(url):
                if url.endswith("fail"):
                    raise ValueError("offline test failure")
                return RSS
            first = module.run(reg, out, fetch)
            second = module.run(reg, out, fetch)
            self.assertEqual(len(first["items"]), 1)
            self.assertEqual(first["coverage"]["successful_feeds"], 1)
            self.assertEqual(first["coverage"]["failed_feeds"], 1)
            self.assertEqual(first["coverage"]["items_missing_named_author"], 1)
            self.assertEqual(len(second["items"]), 1)
            self.assertEqual(second["source_reports"][0]["new"], 0)
            self.assertEqual(second["source_reports"][1]["status"], "error")

if __name__ == "__main__":
    unittest.main()
