import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("authors", Path(__file__).resolve().parents[1] / "scripts/discover_ai_authors.py")
authors = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authors)

class AuthorDiscoveryTests(unittest.TestCase):
    def test_candidates_are_unverified_and_traceable(self):
        sample = {"topic_id": "ai-models", "items": [
            {"url":"https://a.test/1","title":"One","authors":["Alice Example"],"attribution_basis":"entry","source_id":"a","publisher":"A","discovered_from":"https://a.test/feed"},
            {"url":"https://b.test/2","title":"Two","authors":["alice example"],"attribution_basis":"entry","source_id":"b","publisher":"B"},
            {"url":"https://c.test/3","title":"Three","authors":["private@example.org"],"source_id":"c"},
            {"url":"https://c.test/4","title":"Four","authors":[],"source_id":"c"}]}
        result = authors.build_candidates(sample)
        self.assertEqual(result["candidate_count"], 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["identity_status"], "unverified")
        self.assertEqual(candidate["publication_count"], 2)
        self.assertEqual(candidate["source_ids"], ["a","b"])
        self.assertEqual(candidate["discovered_from"], ["https://a.test/feed"])

    def test_feed_level_author_is_not_an_article_byline(self):
        sample = {"items": [
            {"url":"https://example.org/1","authors":["Publisher Owner"],"attribution_basis":"feed"},
            {"url":"https://example.org/2","authors":["Article Writer"],"attribution_basis":"entry"}]}
        result = authors.build_candidates(sample)
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["candidates"][0]["display_name"], "Article Writer")

if __name__ == "__main__":
    unittest.main()
