import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from ingestion.archive import archive_snapshot


class ArchiveTests(unittest.TestCase):
    def test_immutable_and_auditable(self):
        with tempfile.TemporaryDirectory() as directory:
            data = {"connector": "bluesky", "observations": [{"id": "post-1"}]}
            when = datetime(2026, 10, 10, tzinfo=timezone.utc)
            report = archive_snapshot(data, directory, collected_at=when)
            path = Path(report["path"])
            self.assertEqual(json.loads(path.read_text())["observations"], [{"id": "post-1"}])
            self.assertEqual(report["observations"], 1)
            with self.assertRaises(FileExistsError):
                archive_snapshot(data, directory, collected_at=when)

    def test_invalid_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                archive_snapshot({"connector": "../escape", "observations": []}, directory)


if __name__ == "__main__":
    unittest.main()
