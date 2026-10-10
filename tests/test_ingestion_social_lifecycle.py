import unittest
from datetime import datetime, timezone

from ingestion.social_lifecycle import reconciliation_plan, retention_decision


class SocialLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 10, tzinfo=timezone.utc)
        self.post = {"connector": "bluesky", "external_id": "at://did:plc:a/post/1",
                     "collected_at": "2026-10-01T00:00:00Z"}

    def test_retains_recent_post_without_deleting(self):
        result = retention_decision(self.post, now=self.now)
        self.assertEqual(result["action"], "retain_temporarily")

    def test_expiry_and_verified_removal_are_purge_candidates(self):
        self.assertEqual(retention_decision(self.post, now=self.now, max_age_days=5)["action"],
                         "purge_candidate")
        self.assertEqual(retention_decision(self.post, now=self.now,
                         removed_ids={self.post["external_id"]})["reason"],
                         "verified_removal_signal")

    def test_missing_time_is_review_not_silent_retention(self):
        result = retention_decision({"connector": "mastodon", "external_id": "post-1"},
                                    now=self.now)
        self.assertEqual(result["action"], "review")

    def test_non_social_is_not_automatically_purged(self):
        self.assertEqual(retention_decision({"connector": "crossref"}, now=self.now)["action"],
                         "not_applicable")

    def test_plan_is_read_only(self):
        report = reconciliation_plan([self.post], now=self.now)
        self.assertFalse(report["automatic_deletion_performed"])


if __name__ == "__main__":
    unittest.main()
