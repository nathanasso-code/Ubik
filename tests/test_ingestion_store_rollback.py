import tempfile
import unittest
from pathlib import Path

from ingestion.run_batch import run_pages
from ingestion.sqlite_ledger import connect, metrics
from ingestion.sqlite_store import SQLiteStore


class StoreRollbackTests(unittest.TestCase):
    def test_invalid_observation_does_not_advance_cursor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = connect(root / "ledger.sqlite3")
            store = SQLiteStore(db)
            def invalid(_actor, *, limit, cursor):
                self.assertIsNone(cursor)
                return {"connector": "bluesky", "observations": [
                    {"connector": "bluesky", "source_id": "did:plc:a"}],
                    "next_cursor": "page-two"}
            args = dict(source="example.bsky.social", archive_dir=root / "archive",
                        checkpoint_dir=root / "checkpoints", max_pages=1,
                        store=store, sleep=lambda _: None)
            with self.assertRaises(ValueError):
                run_pages("bluesky", fetchers={"bluesky": invalid}, **args)
            self.assertEqual(metrics(db)["pages"], 0)
            def valid(_actor, *, limit, cursor):
                self.assertIsNone(cursor)
                return {"connector": "bluesky", "observations": [
                    {"connector": "bluesky", "source_id": "did:plc:a",
                     "external_id": "at://did:plc:a/app.bsky.feed.post/1"}],
                    "next_cursor": None}
            result = run_pages("bluesky", fetchers={"bluesky": valid}, **args)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(metrics(db)["pages"], 1)
            db.close()


if __name__ == "__main__":
    unittest.main()
