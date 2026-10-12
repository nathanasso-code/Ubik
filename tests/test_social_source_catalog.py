import unittest
from ingestion.social_source_catalog import build_source_candidates, external_links


class SocialSourceCatalogTests(unittest.TestCase):
    def test_social_links_join_existing_catalogue(self):
        posts = [{"url":"https://mastodon.social/@alice/1","author_url":"https://mastodon.social/@alice",
                  "content_html":'<p>Read <a href="https://example.org/study?utm_source=mastodon">paper</a></p>'},
                 {"url":"https://mastodon.social/@bob/2","author_url":"https://mastodon.social/@bob",
                  "content_html":'<a href="https://example.org/study">study</a>'}]
        existing = {"items":[{"url":"https://example.org/study","source_ids":["rss:example"]}]}
        result = build_source_candidates(posts, existing)
        self.assertEqual(result["documents"], 1)
        row = result["items"][0]
        self.assertEqual(row["distinct_social_accounts"], 2)
        self.assertEqual(set(row["discovery_channels"]), {"mastodon","existing_catalogue"})
        self.assertEqual(row["validation"], "not_assessed")

    def test_ignore_social_self_link(self):
        self.assertEqual(external_links({"content_html":'<a href="https://mastodon.social/@x/1">post</a>'}), [])

if __name__ == "__main__":
    unittest.main()
