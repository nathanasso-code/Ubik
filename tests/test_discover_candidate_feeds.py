import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("feeds", Path(__file__).resolve().parents[1] / "scripts/discover_candidate_feeds.py")
feeds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feeds)

class FeedDiscoveryTests(unittest.TestCase):
    def test_parser_recognizes_rss_and_atom(self):
        p = feeds.FeedLinks()
        p.feed('<link rel="alternate" type="application/rss+xml" href="/feed.xml"><link rel="alternate" type="application/atom+xml" href="https://example.org/atom"><link rel="stylesheet" href="/x.css">')
        self.assertEqual(p.links, ["/feed.xml", "https://example.org/atom"])
    @patch.object(feeds, "discover", return_value=["https://example.org/feed"])
    def test_queue_requires_review(self, _):
        result = feeds.run({"candidates": [{"id":"a", "name":"A", "url":"https://example.org"}]})
        self.assertTrue(result["promotion_requires_review"])
        self.assertEqual(result["results"][0]["status"], "found")
    def test_reject_http(self):
        with self.assertRaises(ValueError):
            feeds.discover("http://example.org")

if __name__ == "__main__":
    unittest.main()
