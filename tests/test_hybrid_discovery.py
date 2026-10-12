import unittest
from ingestion.hybrid_document_links import hybrid_links
from ingestion.hashtag_topic_routing import suggest_hashtag_topics
from ingestion.global_social_followup import sample

class HybridDiscoveryTests(unittest.TestCase):
    def test_join_social_only_and_cross_channel_links(self):
        rss={"items":[{"url":"https://a.example/story?utm_source=x","title":"Report","source_id":"publisher"}]}
        social=[{"documents":[{"url":"https://a.example/story","post_urls":["https://bsky.app/p/1"],"providers":["bluesky"]},
                              {"url":"https://b.example/new","post_urls":["https://mastodon.social/p/2"],"providers":["mastodon"]}]}]
        r=hybrid_links(rss,social)
        self.assertEqual(r["cross_channel_document_hints"],1)
        self.assertEqual(r["social_document_hints"],2)
        self.assertEqual(len(r["documents"]),2)
    def test_contextual_routing_requires_multiple_posts_and_abstains(self):
        topics=[{"id":"energy","title":"Energia in Italia","context":"rete elettrica centrali energia elettrica nucleare Italia"}]
        posts=[{"url":f"https://social.example/{i}","source_id":f"account-{i}",
                "title":"#gridoutage blackout nella rete elettrica italiana",
                "metadata":{"hashtags":["gridoutage"],"linked_documents":["https://news.example/grid"]}}
               for i in range(2)]
        r=suggest_hashtag_topics(posts,topics,min_score=0.01)
        self.assertEqual(len(r["suggestions"]),1)
        self.assertEqual(r["suggestions"][0]["topic_id"],"energy")
        self.assertFalse(r["automatic_topic_assignment"])
        self.assertEqual(suggest_hashtag_topics(posts[:1],topics)["suggestions"],[])
    def test_social_queries_derived_only_from_global_candidates(self):
        def fetch(url):
            return {"posts":[]} if "bsky" in url else []
        r=sample({"candidate_terms":[{"term":"riyadh","publisher_hosts":3},
                                     {"term":"singleton","publisher_hosts":1}]},fetch=fetch)
        self.assertEqual(r["queries"],["riyadh"])
        self.assertEqual(r["observations"],[])
if __name__=="__main__":unittest.main()
