import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ingestion.coverage_report import evaluate_coverage
from ingestion.federate import federate
from ingestion.source_inventory import inventory


ROOT = Path(__file__).resolve().parents[1]


class SourceInventoryCoverageTests(unittest.TestCase):
    def test_registry_inventory_is_explicitly_unverified(self):
        result = inventory(ROOT)
        self.assertGreaterEqual(result["registry_entries"], 30)
        self.assertGreaterEqual(result["enabled_rss"], 20)
        self.assertTrue(all(x["readiness"] == "configured_unverified"
                            for x in result["registry"] if x["configured_enabled"]))
        self.assertEqual({p["provider"] for p in result["providers"]},
                         {"rss", "hacker_news", "gdelt", "bluesky",
                          "mastodon", "openalex", "crossref"})

    def test_failed_feed_not_counted_as_empty_success(self):
        catalog = inventory(ROOT)
        discovery = {"source_reports": [
            {"source_id": "openai-news", "status": "error", "error": "HTTP 503"},
            {"source_id": "arxiv-cs-ai", "status": "ok", "seen": 2, "stored": 5}]}
        report = evaluate_coverage(catalog, discovery=discovery)
        self.assertEqual(report["tested_feed_count"], 2)
        self.assertEqual(report["successful_feed_count"], 1)
        self.assertEqual(report["failed_feed_count"], 1)
        by_id = {x["source_id"]: x for x in report["feed_status"]}
        self.assertEqual(by_id["openai-news"]["status"], "error")
        self.assertIsNone(by_id["openai-news"]["seen"])
        self.assertEqual(by_id["arxiv-cs-ai"]["stored"], 5)
        self.assertEqual(by_id["arxiv-cs-ai"]["note"],
                         "cumulative_stored_not_current_fetch")

    def test_unselected_observations_keep_duplicate_and_missing_date(self):
        observation = {"connector": "bluesky", "source_id": "actor",
                       "external_id": "post-1", "url": "https://example.org/p",
                       "canonical_url_hint": "https://example.org/p"}
        report = evaluate_coverage(
            inventory(ROOT), federated={"observations": [observation, observation]},
            now=datetime(2026, 10, 10, tzinfo=timezone.utc))
        self.assertEqual(report["observations_audited"], 2)
        self.assertEqual(report["duplicate_diagnostics"]["extra_repeated_observations"], 1)
        self.assertEqual(report["source_observations"][0]["missing_publication_dates"], 2)
        self.assertEqual(report["tested_feed_count"], 0)


if __name__ == "__main__":
    unittest.main()
