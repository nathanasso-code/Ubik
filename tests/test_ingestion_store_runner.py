import tempfile
import unittest
from pathlib import Path

from ingestion.run_batch import run_pages
from ingestion.sqlite_ledger import connect, metrics
from ingestion.sqlite_store import SQLiteStore


class StoreRunnerTests(unittest.TestCase):
    def test_explicit_store_resumes_and_rejects_mixed_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = connect(root / "ledger.sqlite3")
            store = SQLiteStore(db)
            seen = []
            def fetch(_actor, *, limit, cursor):
                seen.append(cursor)
                return {"connector": "bluesky", "observations": [],
                        "next_cursor": "next" if cursor is None else None}
            opts = dict(source="example.bsky.social", archive_dir=root / "a",
                        checkpoint_dir=root / "c", max_pages=1,
                        fetchers={"bluesky": fetch}, sleep=lambda _: None)
            first = run_pages("bluesky", store=store, **opts)
            self.assertEqual(first["status"], "budget_exhausted")
            second = run_pages("bluesky", store=store, **opts)
            self.assertEqual(second["status"], "completed")
            self.assertEqual(seen, [None, "next"])
            self.assertEqual(metrics(db)["pages"], 2)
            self.assertFalse((root / "c").exists())
            with self.assertRaises(ValueError):
                run_pages("bluesky", store=store, ledger=db, **opts)
            db.close()


if __name__ == "__main__":
    unittest.main()
