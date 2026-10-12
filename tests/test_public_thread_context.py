import unittest
from ingestion.public_thread_context import bluesky_thread, bluesky_thread_url, mastodon_context, mastodon_context_url

class PublicThreadContextTests(unittest.TestCase):
    def test_bluesky_replies_without_text(self):
        root="at://did:plc:one/app.bsky.feed.post/abc"
        child="at://did:plc:two/app.bsky.feed.post/def"
        payload={"thread":{"post":{"uri":root,"author":{"did":"did:plc:one"},"replyCount":1},
                "replies":[{"post":{"uri":child,"author":{"did":"did:plc:two"}}}]}}
        result=bluesky_thread(root,fetch=lambda url:payload)
        self.assertEqual(result["posts_visible"],2)
        self.assertEqual(result["unique_authors_visible"],2)
        self.assertTrue(all("text" not in x for x in result["items"]))
        self.assertEqual(result["quality"],"not_assessed")

    def test_mastodon_context(self):
        url="https://mastodon.social/@alice/123"
        self.assertEqual(mastodon_context_url(url),
                         "https://mastodon.social/api/v1/statuses/123/context")
        result=mastodon_context(url,fetch=lambda _:{"ancestors":[],"descendants":[
            {"id":"456","url":"https://mastodon.social/@bob/456","account":{"acct":"bob"},"in_reply_to_id":"123"}]})
        self.assertEqual(len(result["replies"]),1)
        self.assertNotIn("content",result["replies"][0])

    def test_bad_urls(self):
        with self.assertRaises(ValueError):
            bluesky_thread_url("https://bsky.app/profile/a/post/123")
        with self.assertRaises(ValueError):
            mastodon_context_url("https://localhost/@alice/123")

if __name__=="__main__":
    unittest.main()
