import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ingestion.locks import SourceBusyError, source_lock
from ingestion.run_batch import run_pages


class SourceLockTests(unittest.TestCase):
    def test_rejects_same_scope_until_released(self):
        with tempfile.TemporaryDirectory() as directory:
            with source_lock(directory, "provider-source"):
                with self.assertRaises(SourceBusyError):
                    with source_lock(directory, "provider-source"):
                        pass
                with source_lock(directory, "other-source"):
                    pass
            with source_lock(directory, "provider-source"):
                pass

    def test_runner_rejects_competing_worker_before_fetch(self):
        calls = []
        def fake(actor, *, limit, cursor):
            calls.append(cursor)
            return {"connector": "bluesky", "observations": [],
                    "next_cursor": None}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def overlapping(*args, **kwargs):
                with self.assertRaises(SourceBusyError):
                    run_pages("bluesky", source="example.bsky.social",
                              archive_dir=root / "archives",
                              checkpoint_dir=root / "checkpoints",
                              max_pages=1, fetchers={"bluesky": fake})
                return fake(*args, **kwargs)
            result = run_pages("bluesky", source="example.bsky.social",
                               archive_dir=root / "archives",
                               checkpoint_dir=root / "checkpoints",
                               max_pages=1, fetchers={"bluesky": overlapping})
            self.assertEqual(result["pages"], 1)
            self.assertEqual(calls, [None])


if __name__ == "__main__":
    unittest.main()
