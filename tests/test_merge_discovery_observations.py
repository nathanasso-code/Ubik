import unittest
from scripts.merge_discovery_observations import canonical_url, merge_observations


class DiscoveryMergeTests(unittest.TestCase):
    def test_tracking_removed_but_content_query_preserved(self):
        self.assertEqual(canonical_url("https://EXAMPLE.org/story?utm_source=x&id=7#part"),
                         "https://example.org/story?id=7")

    def test_duplicate_document_retains_both_observations(self):
        result = merge_observations([
            ("rss", [{"id": "r1", "url": "https://a.org/x?utm_source=rss", "source_id": "publisher"}]),
            ("social", [{"id": "s1", "url": "https://a.org/x", "source_id": "hacker-news"}]),
        ])
        self.assertEqual(len(result["documents"]), 1)
        self.assertEqual(result["documents"][0]["observation_count"], 2)
        self.assertEqual(result["documents"][0]["independent_confirmation"], "not_assessed")
        self.assertEqual({x["origin"] for x in result["documents"][0]["observations"]}, {"rss", "social"})

    def test_different_urls_remain_distinct(self):
        result = merge_observations([("rss", [{"url": "https://a.org/a"}, {"url": "https://a.org/b"}])])
        self.assertEqual(len(result["documents"]), 2)

    def test_invalid_isolated(self):
        result = merge_observations([("rss", [{"title": "missing URL"}, {"url": "https://a.org"}])])
        self.assertEqual(len(result["invalid_observations"]), 1)


if __name__ == "__main__":
    unittest.main()
