import unittest
from pathlib import Path

from ingestion.channel_readiness import assess_channels
from ingestion.cross_topic_inventory import cross_topic_inventory
from ingestion.feed_triage import triage_feed_reports


ROOT = Path(__file__).resolve().parents[1]


class ExpandedSourceAuditTests(unittest.TestCase):
    def test_candidate_sources_remain_disabled(self):
        result = cross_topic_inventory(ROOT)
        self.assertEqual(result["counts_by_origin"]["ai_models_pilot"], 32)
        self.assertEqual(result["counts_by_origin"]["italian_candidate"], 12)
        self.assertEqual(result["total_entries"], 44)
        italian = [x for x in result["sources"] if x["origin"] == "italian_candidate"]
        self.assertTrue(all(not x["acquisition_enabled"] for x in italian))
        self.assertIn("youtube_transcripts", result["unrepresented_channels"])

    def test_provider_evidence_is_not_continuous_coverage(self):
        report = assess_channels(cross_topic_inventory(ROOT))
        by_name = {x["provider"]: x for x in report["channels"]}
        self.assertEqual(by_name["mastodon"]["last_evidence_status"], "http_422_unresolved")
        self.assertFalse(any(x["continuous_coverage_verified"] for x in report["channels"]))
        self.assertEqual(by_name["hacker_news"]["last_evidence_status"], "not_tested")

    def test_failure_triage_preserves_upstream_empty_and_safety(self):
        report = triage_feed_reports([
            {"source_id": "a", "status": "error", "error": "HTTP Error 403: Forbidden"},
            {"source_id": "b", "status": "error", "error": "Feed exceeds limit"},
            {"source_id": "c", "status": "ok", "raw_entries": 0, "seen": 0},
            {"source_id": "d", "status": "ok", "raw_entries": 5, "seen": 3},
            {"source_id": "e", "status": "ok", "raw_entries": 5, "seen": 5},
        ])
        self.assertEqual([x["issue"] for x in report["issues"]],
                         ["http_403", "payload_limit", "upstream_zero_entries", "normalization_loss"])
        self.assertTrue(all(not x["access_change_authorized"] for x in report["issues"]))


if __name__ == "__main__":
    unittest.main()
