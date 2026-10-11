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

    def test_raw_entries_can_exceed_normalized_entries(self):
        invalid = b'<rss><channel><item><title>No link</title></item><item><title>Valid</title><link>https://example.org/valid</link></item></channel></rss>'
        self.assertEqual(module.raw_feed_entry_count(invalid), 2)
        self.assertEqual(len(module.parse_feed(invalid, {"id": "x", "name": "X"})), 1)

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

    def test_shared_url_keeps_each_source_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, out = Path(tmp)/"registry.json", Path(tmp)/"result.json"
            reg.write_text(json.dumps({"topic_id": "ai-models", "sources": [
                {"id": "first", "name": "First", "url": "https://first.example/feed", "enabled": True, "kind": "rss"},
                {"id": "second", "name": "Second", "url": "https://second.example/feed", "enabled": True, "kind": "rss"}
            ]}))
            first = module.run(reg, out, lambda url: RSS)
            self.assertEqual(len(first["items"]), 2)
            self.assertEqual(first["coverage"]["stored_items"], 2)
            self.assertEqual(first["coverage"]["unique_article_urls"], 1)
            self.assertEqual({item["source_id"] for item in first["items"]}, {"first", "second"})
            self.assertEqual(len({item["url"] for item in first["items"]}), 1)
            self.assertEqual([row["stored"] for row in first["source_reports"]], [1, 1])
            again = module.run(reg, out, lambda url: RSS)
            self.assertEqual(len(again["items"]), 2)
            self.assertEqual([row["new"] for row in again["source_reports"]], [0, 0])

    def test_arxiv_empty_daily_feed_uses_bounded_official_atom_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, out = Path(tmp)/"registry.json", Path(tmp)/"result.json"
            primary = "https://rss.arxiv.org/rss/cs.AI"
            fallback = "https://export.arxiv.org/api/query?search_query=cat%3Acs.AI&max_results=30"
            reg.write_text(json.dumps({"topic_id": "ai-models", "sources": [
                {"id": "arxiv-cs-ai", "name": "arXiv", "url": primary,
                 "empty_feed_fallback_url": fallback, "enabled": True, "kind": "rss"}]}))
            called = []
            def fetch(url):
                called.append(url)
                return b"<rss><channel></channel></rss>" if url == primary else ATOM
            result = module.run(reg, out, fetch)
            self.assertEqual(called, [primary, fallback])
            self.assertEqual(len(result["items"]), 1)
            self.assertTrue(result["source_reports"][0]["fallback_used"])
            self.assertEqual(result["items"][0]["discovered_from"], fallback)

    def test_arxiv_nonempty_rss_does_not_call_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, out = Path(tmp)/"registry.json", Path(tmp)/"result.json"
            reg.write_text(json.dumps({"topic_id": "ai-models", "sources": [
                {"id": "arxiv-cs-ai", "name": "arXiv", "url": "https://rss.arxiv.org/rss/cs.AI",
                 "empty_feed_fallback_url": "https://export.arxiv.org/api/query?max_results=30",
                 "enabled": True, "kind": "rss"}]}))
            called = []
            def fetch(url):
                called.append(url)
                return RSS
            result = module.run(reg, out, fetch)
            self.assertEqual(len(called), 1)
            self.assertFalse(result["source_reports"][0]["fallback_used"])

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
            self.assertEqual(first["source_reports"][0]["raw_entries"], 1)
            self.assertEqual(first["coverage"]["failed_feeds"], 1)
            self.assertEqual(first["coverage"]["items_missing_named_author"], 1)
            self.assertEqual(len(second["items"]), 1)
            self.assertEqual(second["source_reports"][0]["new"], 0)
            self.assertEqual(second["source_reports"][1]["status"], "error")

if __name__ == "__main__":
    unittest.main()
