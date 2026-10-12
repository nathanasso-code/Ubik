import unittest
from ingestion.topic_quality_views import topic_views


class TopicQualityViewsTests(unittest.TestCase):
    def test_three_nested_views_with_review_gate(self):
        docs = [
            {"url":"https://example.org/a","topic_ids":["ai"],"discovery_channels":["mastodon"],"distinct_social_accounts":4},
            {"url":"https://example.org/b","topic_ids":["ai"],"discovery_channels":["rss"],"editorial_essential_approved":True,"documentary_validation":"reviewed"},
            {"url":"https://example.org/c","topic_ids":["ai"],"discovery_channels":["gdelt"]},
            {"url":"https://example.org/d","topic_ids":["other"],"discovery_channels":["mastodon"],"distinct_social_accounts":99},
        ]
        result=topic_views(docs,topic_id="ai",explore_limit=1,relevant_limit=1)
        views=result["views"]
        urls={k:{x["url"] for x in v} for k,v in views.items()}
        self.assertEqual(urls["essenziali"],{"https://example.org/b"})
        self.assertTrue(urls["essenziali"] <= urls["rilevanti"] <= urls["esplora"])
        self.assertNotIn("https://example.org/d",urls["esplora"])

    def test_attention_alone_cannot_validate(self):
        result=topic_views([{"url":"https://example.org/a","topic_ids":["ai"],
                            "distinct_social_accounts":10000,"discovery_channels":["mastodon"]}],topic_id="ai")
        self.assertEqual(result["counts"]["essenziali"],0)
        self.assertEqual(result["counts"]["rilevanti"],1)

if __name__=="__main__":
    unittest.main()
