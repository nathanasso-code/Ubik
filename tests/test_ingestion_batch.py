import tempfile
import unittest
from pathlib import Path
from ingestion.checkpoints import read_checkpoint, write_checkpoint
from ingestion.run_batch import run_pages


class CheckpointTests(unittest.TestCase):
    def test_atomic_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            value = write_checkpoint(directory, "source-1", cursor="next",
                                     archive_sha256="a" * 64, archive_path="snapshot.json")
            self.assertEqual(read_checkpoint(directory, "source-1"), value)

    def test_rejects_traversal(self):
        with self.assertRaises(ValueError):
            read_checkpoint("/tmp", "../other")


class BatchRunnerTests(unittest.TestCase):
    def test_resumes_without_refetching_first_page(self):
        calls = []
        def fake(actor, *, limit, cursor):
            calls.append(cursor)
            return {"connector": "bluesky",
                    "observations": [{"id": f"post-{len(calls)}"}],
                    "next_cursor": "next" if cursor is None else None}
        with tempfile.TemporaryDirectory() as directory:
            archives = Path(directory) / "archives"
            checkpoints = Path(directory) / "checkpoints"
            first = run_pages("bluesky", source="example.bsky.social",
                              archive_dir=archives, checkpoint_dir=checkpoints,
                              max_pages=1, fetchers={"bluesky": fake}, sleep=lambda _: None)
            self.assertEqual(first["status"], "budget_exhausted")
            second = run_pages("bluesky", source="example.bsky.social",
                               archive_dir=archives, checkpoint_dir=checkpoints,
                               max_pages=2, fetchers={"bluesky": fake}, sleep=lambda _: None)
            self.assertEqual(calls, [None, "next"])
            self.assertEqual(second["status"], "completed")
            self.assertEqual(len(list(archives.glob("*.json"))), 2)
            third = run_pages("bluesky", source="example.bsky.social",
                              archive_dir=archives, checkpoint_dir=checkpoints,
                              fetchers={"bluesky": fake}, sleep=lambda _: None)
            self.assertEqual(third["pages"], 0)

    def test_failure_does_not_advance_checkpoint(self):
        def broken(*_args, **_kwargs):
            raise OSError("API down")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                run_pages("mastodon", source="example.social", archive_dir=Path(directory) / "a",
                          checkpoint_dir=Path(directory) / "c",
                          fetchers={"mastodon": broken}, sleep=lambda _: None)
            self.assertEqual(list((Path(directory) / "c").glob("*.json")), [])

    def test_page_budget(self):
        with self.assertRaises(ValueError):
            run_pages("bluesky", source="example.bsky.social", archive_dir="/tmp/a",
                      checkpoint_dir="/tmp/c", max_pages=21)


if __name__ == "__main__":
    unittest.main()
