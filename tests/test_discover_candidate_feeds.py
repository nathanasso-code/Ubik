import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

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
    @patch.object(feeds.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 443))])
    def test_reject_loopback_dns(self, _):
        with self.assertRaisesRegex(ValueError, "non-public"):
            feeds.discover("https://example.org")

    @patch.object(feeds.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.215.14", 443))])
    @patch.object(feeds.urllib.request, "build_opener")
    def test_redirects_disabled(self, build_opener, _):
        build_opener.return_value.open.side_effect = ValueError("Redirect requires separate review")
        with self.assertRaisesRegex(ValueError, "Redirect"):
            feeds.discover("https://example.org")
        self.assertEqual(build_opener.call_args.args[0], feeds.NoRedirect)

    def test_reject_credentials(self):
        with self.assertRaises(ValueError):
            feeds.discover("https://user:password@example.org/")

    @patch.object(feeds.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.215.14", 443))])
    @patch.object(feeds.urllib.request, "build_opener")
    def test_page_size_limit(self, build_opener, _):
        response = MagicMock()
        response.geturl.return_value = "https://example.org"
        response.read.return_value = b"x" * 512001
        build_opener.return_value.open.return_value.__enter__.return_value = response
        with self.assertRaisesRegex(ValueError, "size limit"):
            feeds.discover("https://example.org")

    @patch.object(feeds.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.215.14", 443))])
    @patch.object(feeds.urllib.request, "build_opener")
    def test_feed_links_keep_only_https_without_credentials(self, build_opener, _):
        response = MagicMock()
        response.geturl.return_value = "https://example.org/start"
        response.read.return_value = (b'<link rel="alternate" type="application/rss+xml" href="/rss">'
                                      b'<link rel="alternate" type="application/rss+xml" href="http://example.org/insecure">'
                                      b'<link rel="alternate" type="application/rss+xml" href="https://u:p@example.org/private">')
        build_opener.return_value.open.return_value.__enter__.return_value = response
        self.assertEqual(feeds.discover("https://example.org/start"), ["https://example.org/rss"])

    def test_reject_http(self):
        with self.assertRaises(ValueError):
            feeds.discover("http://example.org")

if __name__ == "__main__":
    unittest.main()
