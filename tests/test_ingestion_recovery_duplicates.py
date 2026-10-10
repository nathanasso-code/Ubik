import tempfile
import unittest
from pathlib import Path

from ingestion.duplicates import duplicate_report
from ingestion.run_batch import run_pages
from ingestion.checkpoints import read_checkpoint


class DuplicateAccountingTests(unittest.TestCase):
    def test_repeat_identities_remain_and_are_counted(self):
        base = {"connector": "crossref", "source_id": "crossref-works",
                "external_id": "10.1000/a", "canonical_url_hint": "https://doi.org/10.1000/a"}
        observations = [
            {**base, "snapshot": "page-1"},
            {**base, "snapshot": "page-2"},
            {**base, "external_id": "10.1000/b", "snapshot": "page-2"}]
        report = duplicate_report({"observations": observations})
        self.assertEqual(report["total_observations"], 3)
        self.assertEqual(report["unique_provider_identities"], 2)
        self.assertEqual(report["extra_repeated_observations"], 1)
        self.assertEqual(report["identities_repeated_across_snapshots"], 1)
        self.assertFalse(report["deduplication_applied"])


class CrashRecoveryTests(unittest.TestCase):
    def test_archive_write_failure_does_not_advance_checkpoint(self):
        calls = []
        def fetch(actor, *, limit, cursor):
            calls.append(cursor)
            return {"connector": "bluesky", "observations": [{"id": "same"}],
                    "next_cursor": "page-2" if cursor is None else None}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a, c = root / "archives", root / "checkpoints"
            first = run_pages("bluesky", source="example.bsky.social",
                              archive_dir=a, checkpoint_dir=c, max_pages=1,
                              fetchers={"bluesky": fetch}, sleep=lambda _: None)
            cp = read_checkpoint(c, first["checkpoint"])
            # Make the next archive write fail before checkpoint advancement.
            from unittest.mock import patch
            with patch("ingestion.run_batch.archive_snapshot", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    run_pages("bluesky", source="example.bsky.social",
                              archive_dir=a, checkpoint_dir=c, max_pages=1,
                              fetchers={"bluesky": fetch}, sleep=lambda _: None)
            self.assertEqual(read_checkpoint(c, first["checkpoint"]), cp)
            final = run_pages("bluesky", source="example.bsky.social",
                              archive_dir=a, checkpoint_dir=c, max_pages=1,
                              fetchers={"bluesky": fetch}, sleep=lambda _: None)
            self.assertEqual(final["status"], "completed")
            self.assertEqual(calls, [None, "page-2", "page-2"])


if __name__ == "__main__":
    unittest.main()
