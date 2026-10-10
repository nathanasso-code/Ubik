import unittest
from datetime import datetime, timezone

from ingestion.source_quality import acquisition_quality


class SourceQualityTests(unittest.TestCase):
    def test_per_source_duplicates_and_rss_freshness(self):
        items = [
            {"connector": "rss", "source_id": "a", "external_id": "x",
             "published_raw": "Thu, 08 Oct 2026 10:00:00 GMT", "metadata": {}},
            {"connector": "rss", "source_id": "a", "external_id": "x",
             "published_raw": "Thu, 08 Oct 2026 10:00:00 GMT", "metadata": {}},
            {"connector": "rss", "source_id": "b", "external_id": "x",
             "published_raw": None, "metadata": {}},
        ]
        report = acquisition_quality({"observations": items},
                                     now=datetime(2026, 10, 10, tzinfo=timezone.utc))
        self.assertEqual(report["total_observations"], 3)
        self.assertEqual(report["by_source"][0]["duplicate_extra_observations"], 1)
        self.assertEqual(report["by_source"][0]["freshness"]["within_7d"], 2)
        self.assertEqual(report["by_source"][1]["freshness"]["unknown"], 1)
        self.assertIsNone(report["global_recall"])
        self.assertTrue(all(row["estimated_recall"] is None for row in report["by_source"]))


if __name__ == "__main__":
    unittest.main()
