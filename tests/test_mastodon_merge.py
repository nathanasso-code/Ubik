import unittest
from ingestion.mastodon_merge import merge_discoveries


class MergeTests(unittest.TestCase):
    def test_cross_instance_same_activitypub_uri(self):
        def record(url, source, tags):
            return {"connector": "mastodon", "external_id": "https://origin.social/users/a/statuses/7",
                    "url": url, "discovered_from": source, "metadata": {"tags": tags},
                    "editorial_selection": "not_assessed"}
        pages = [
            {"connector": "mastodon", "observations": [record("https://one.social/@a/7", "https://one.social/tag/science", ["science"])]},
            {"connector": "mastodon", "observations": [record("https://two.social/@a/7", "https://two.social/tag/ai", ["ai"])]},
        ]
        merged = merge_discoveries(pages)
        self.assertEqual(merged["raw_observation_count"], 2)
        self.assertEqual(merged["unique_observation_count"], 1)
        item = merged["observations"][0]
        self.assertEqual(len(item["discovered_via"]), 2)
        self.assertEqual(item["metadata"]["tags"], ["science", "ai"])
        self.assertEqual(item["alternate_urls"], ["https://two.social/@a/7"])
        self.assertEqual(item["editorial_selection"], "not_assessed")

    def test_no_false_merging_different_statuses(self):
        base = {"connector": "mastodon", "url": "https://a.social/1", "metadata": {}}
        a = dict(base, external_id="https://a.social/1")
        b = dict(base, external_id="https://a.social/2")
        result = merge_discoveries([{"connector": "mastodon", "observations": [a, b]}])
        self.assertEqual(result["unique_observation_count"], 2)


if __name__ == "__main__":
    unittest.main()
