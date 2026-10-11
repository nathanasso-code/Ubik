import unittest
from ingestion.topic_feed_preview import render


class TopicFeedPreviewTests(unittest.TestCase):
    def test_escapes_titles_and_shows_review_only_status(self):
        report = {"topic": {"name": "AI"}, "candidate_documents": 2, "feed_limit": 30,
                  "visible": [{"url": "https://example.org/?a=1&b=2",
                               "title": "<script>bad</script>", "publisher": "Source",
                               "source_ids": ["source-a"], "area_ids": ["ricerca-e-valutazione"]}]}
        page = render(report)
        self.assertIn("&lt;script&gt;bad&lt;/script&gt;", page)
        self.assertNotIn("<script>bad</script>", page)
        self.assertIn("a=1&amp;b=2", page)
        self.assertIn("nessuna pubblicazione automatica", page)
        self.assertIn("source-a", page)


if __name__ == "__main__":
    unittest.main()
