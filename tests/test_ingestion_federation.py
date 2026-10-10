import unittest
from ingestion.budgets import SourceBudget
from ingestion.legacy_adapters import rss_to_observation, hacker_news_to_observation
from ingestion.federate import federate


class BudgetTests(unittest.TestCase):
    def test_enforces_request_limit(self):
        budget = SourceBudget("a", max_requests=1, max_observations=10)
        budget.record_request()
        self.assertFalse(budget.may_request())
        with self.assertRaises(RuntimeError):
            budget.record_request()

    def test_enforces_observation_limit(self):
        budget = SourceBudget("a", max_requests=3, max_observations=2)
        budget.record_result(2)
        with self.assertRaises(RuntimeError):
            budget.record_result(1)
        self.assertEqual(budget.report()["editorial_decisions"], 0)


class FederationTests(unittest.TestCase):
    def test_adapters_do_not_select_or_cluster(self):
        rss = {"id": "r1", "source_id": "publisher", "title": "A",
               "url": "https://a.org/story?utm_source=rss"}
        hn = {"id": "hn-7", "source_id": "hacker-news-newstories",
              "title": "A", "url": "https://a.org/story",
              "original_url": "https://news.ycombinator.com/item?id=7"}
        result = federate([
            ("rss.json", {"items": [rss]}),
            ("hn.json", {"connector": "hacker_news_newstories", "observations": [hn]}),
        ])
        self.assertEqual(result["metrics"]["observations"], 2)
        self.assertEqual(result["metrics"]["distinct_url_hints"], 1)
        self.assertEqual(result["metrics"]["duplicate_url_observations"], 1)
        self.assertFalse(result["selection_applied"])
        self.assertFalse(result["clustering_applied"])
        self.assertEqual({x["connector"] for x in result["observations"]}, {"rss", "hacker_news"})

    def test_social_science_snapshots_supported(self):
        result = federate([
            ("bluesky.json", {"connector": "bluesky", "observations": [
                {"connector": "bluesky", "source_id": "did:plc:abc",
                 "url": "https://bsky.app/profile/did:plc:abc/post/1"}]}),
            ("openalex.json", {"connector": "openalex", "observations": [
                {"connector": "openalex", "source_id": "openalex-works",
                 "url": "https://doi.org/10.1000/xyz"}]})
        ])
        self.assertEqual(result["metrics"]["observations"], 2)
        self.assertEqual(result["metrics"]["connector_source_pairs"], 2)

    def test_unknown_snapshot_isolated(self):
        result = federate([("bad.json", {"foo": []})])
        self.assertEqual(result["metrics"]["errors"], 1)
        self.assertEqual(result["observations"], [])


if __name__ == "__main__":
    unittest.main()
