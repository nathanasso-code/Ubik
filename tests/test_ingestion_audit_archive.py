import tempfile
import unittest
from pathlib import Path
from ingestion.archive import archive_snapshot
from ingestion.audit_archive import audit_directory


class AuditArchiveTests(unittest.TestCase):
    def test_end_to_end_offline_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            archive_snapshot({"connector": "bluesky", "observations": [
                {"connector": "bluesky", "source_id": "did:plc:alice",
                 "external_id": "at://did:plc:alice/app.bsky.feed.post/1",
                 "url": "https://bsky.app/profile/did:plc:alice/post/1",
                 "published_raw": "2026-10-10T10:00:00Z"}]}, directory)
            output = Path(directory).parent / ("ubik-audit-" + Path(directory).name + ".json")
            try:
                report = audit_directory(directory, output=output)
                self.assertEqual(report["snapshot_files"], 1)
                self.assertEqual(report["total_observations"], 1)
                self.assertEqual(report["by_connector"], {"bluesky": 1})
                self.assertTrue(output.exists())
            finally:
                output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
