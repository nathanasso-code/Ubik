import unittest
from ingestion.broad_source_preview import render


class BroadSourcePreviewTests(unittest.TestCase):
    def test_escapes_untrusted_feed_text_and_keeps_all_sources(self):
        page = render({"items": [
            {"url": "https://example.org/?a=1&b=2",
             "title": "<script>alert(1)</script>", "source_ids": ["lab"],
             "description": "<img src=x onerror=alert(1)>",
             "relevance_hint": "needs_topic_review"},
            {"url": "https://example.org/second", "title": "Other source",
             "source_ids": ["press"], "relevance_hint": "explicit_ai_signal"}]})
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn("<img src=x onerror=alert(1)>", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("https://example.org/?a=1&amp;b=2", page)
        self.assertIn("Other source", page)
        self.assertIn("rows.length", page)


if __name__ == "__main__":
    unittest.main()
