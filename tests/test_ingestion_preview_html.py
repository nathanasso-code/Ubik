import unittest
from ingestion.preview_html import render


class PreviewTests(unittest.TestCase):
    def test_preview_escapes_untrusted_feed_html(self):
        payload = {
            "retrieved_at": "2026-10-11T00:00:00Z",
            "items": [{"source_id": "s", "publisher": "Publisher", "title": '<script>alert(1)</script>',
                       "description": '<img src=x onerror=alert(1)>',
                       "url": "https://example.org/?q=1&x=2", "published_raw": "2026-10-11"}],
            "source_reports": [{"source_id": "s", "status": "ok", "seen": 1}],
        }
        page = render(payload)
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("q=1&amp;x=2", page)
        self.assertIn("1 osservazioni", page)

    def test_preview_rejects_missing_items(self):
        with self.assertRaises(ValueError):
            render({"source_reports": []})


if __name__ == "__main__":
    unittest.main()
