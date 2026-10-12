import unittest
from ingestion.topic_social_discovery import topic_queries, discover

class TopicSocialDiscoveryTests(unittest.TestCase):
    def test_terms_are_topic_based(self):
        self.assertEqual(topic_queries("Guerra russo-ucraina",["Ukraine","Ukraine","Україна"]),
                         ["Guerra russo-ucraina","Ukraine","Україна"])

    def test_discovery_ranks_shared_documents_without_seed_event(self):
        def fake(url):
            if "searchPosts" in url:
                return {"posts":[{"uri":"at://did:plc:one/app.bsky.feed.post/1",
                    "author":{"did":"did:plc:one"},
                    "record":{"text":"https://example.org/story"}},
                    {"uri":"at://did:plc:two/app.bsky.feed.post/2",
                    "author":{"did":"did:plc:two"},
                    "record":{"text":"https://example.org/story"}}]}
            return []
        result=discover("Ukraine",instances=("mastodon.social",),fetch=fake)
        self.assertEqual(result["posts"],2)
        self.assertEqual(result["documents"][0]["distinct_accounts_observed"],2)
        self.assertEqual(result["documents"][0]["url"],"https://example.org/story")
        self.assertFalse(result["errors"])

    def test_errors_are_not_zero_observations(self):
        def failing(_):
            raise RuntimeError("network")
        result=discover("Ukraine",fetch=failing)
        self.assertEqual(len(result["errors"]),2)
        self.assertEqual(result["posts"],0)

if __name__=="__main__":
    unittest.main()
