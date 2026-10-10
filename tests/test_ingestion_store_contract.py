import tempfile
import unittest
from pathlib import Path

from ingestion.sqlite_ledger import LeaseBusyError, connect, metrics
from ingestion.sqlite_store import SQLiteStore


class StoreContractTests(unittest.TestCase):
    def test_acquire_commit_release_and_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            db = connect(Path(directory) / "ledger.sqlite3")
            store = SQLiteStore(db)
            lease = store.acquire("source-scope")
            self.assertIsNone(lease.cursor)
            with self.assertRaises(LeaseBusyError):
                store.acquire("source-scope")
            page = {"observations": [{"connector": "crossref",
                                      "source_id": "crossref-works",
                                      "external_id": "10.1/example"}]}
            store.commit(lease, page, "next-page")
            store.release(lease)
            resumed = store.acquire("source-scope")
            self.assertEqual(resumed.cursor, "next-page")
            self.assertGreater(resumed.epoch, lease.epoch)
            with self.assertRaises(LeaseBusyError):
                store.commit(lease, page, "stale")
            self.assertEqual(metrics(db)["pages"], 1)
            store.release(resumed)
            db.close()


if __name__ == "__main__":
    unittest.main()
