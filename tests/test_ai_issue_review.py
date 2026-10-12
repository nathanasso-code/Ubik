import unittest
from ingestion.ai_issue_review import review_ai_topic


class AiIssueReviewTests(unittest.TestCase):
    def test_perspectives_not_confirmation(self):
        result = review_ai_topic({"topic": "ai", "sources": [{
            "url": "https://example.org/paper", "title": "Paper on agents",
            "author": "Researcher", "summary": "Editorial note",
            "posts": [{"url": "https://bsky.app/profile/a/post/123", "kind": "critica",
                       "author": "a", "summary": "Disagreement"}]
        }]})
        item = result["items"][0]
        self.assertEqual(item["origin"]["primary_status"], "not_assessed")
        self.assertEqual(item["external_perspectives"][0]["independent_confirmation"], False)
        self.assertIsNone(item["card"]["summary"])
        self.assertEqual(item["publication"], "blocked")

    def test_dedup_and_limit(self):
        source = {"url": "https://example.org/a", "title": "Article"}
        result = review_ai_topic({"topic": "ai", "sources": [source, source]}, limit=1)
        self.assertEqual(result["source_count"], 1)
        self.assertEqual(result["candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
