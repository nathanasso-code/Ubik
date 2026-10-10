import unittest
from datetime import datetime, timezone
from ingestion.audit import audit


class AuditTests(unittest.TestCase):
    def test_counts_overlap_without_claiming_independence(self):
        data = {"observations": [
            {"connector": "rss", "source_id": "paper", "external_id": "1",
             "url": "https://example.org/a", "canonical_url_hint": "https://example.org/a",
             "published_raw": "2026-10-10T12:00:00Z"},
            {"connector": "hacker_news", "source_id": "hn", "external_id": "2",
             "url": "https://example.org/a", "canonical_url_hint": "https://example.org/a",
             "published_raw": None},
            {"connector": "rss", "source_id": "paper", "external_id": "1",
             "url": "https://example.org/a", "canonical_url_hint": "https://example.org/a",
             "published_raw": "2026-10-10T12:00:00Z"},
        ]}
        report = audit(data, now=datetime(2026, 10, 10, 13, tzinfo=timezone.utc))
        self.assertEqual(report["total_observations"], 3)
        self.assertEqual(report["distinct_url_hints"], 1)
        self.assertEqual(report["overlap"]["url_hints_multiple_connectors"], 1)
        self.assertEqual(report["freshness"]["within_24h"], 2)
        self.assertEqual(report["freshness"]["unknown_or_unparseable"], 1)
        self.assertEqual(report["unique_external_ids_by_source"][1]["count"], 1)
        self.assertIn("not evidence", report["interpretation"])

    def test_future_timestamps_not_counted_as_fresh(self):
        report = audit({"observations": [
            {"connector": "rss", "source_id": "s", "published_raw": "2027-01-01T00:00:00Z"}]},
            now=datetime(2026, 10, 10, tzinfo=timezone.utc))
        self.assertEqual(report["freshness"]["future_timestamp"], 1)


if __name__ == "__main__":
    unittest.main()
