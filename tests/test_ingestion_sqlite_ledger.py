import tempfile
import unittest
from pathlib import Path

from ingestion.sqlite_ledger import (LeaseBusyError, acquire, commit_page,
                                     connect, metrics, release)


class SQLiteLedgerTests(unittest.TestCase):
    def test_lease_transaction_replay_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite3"
            db = connect(path)
            self.assertIsNone(acquire(db, "crossref-window", "worker-a", now=10, ttl=30))
            with self.assertRaises(LeaseBusyError):
                acquire(db, "crossref-window", "worker-b", now=11)
            snapshot = {"connector": "crossref", "observations": [
                {"connector": "crossref", "source_id": "crossref-works",
                 "external_id": "10.1234/a", "url": "https://doi.org/10.1234/a"}]}
            first = commit_page(db, "crossref-window", "worker-a", snapshot, "cursor-2", now=12)
            self.assertTrue(first["new_page"])
            again = commit_page(db, "crossref-window", "worker-a", snapshot, "cursor-2", now=13)
            self.assertFalse(again["new_page"])
            with self.assertRaises(LeaseBusyError):
                commit_page(db, "crossref-window", "worker-b", snapshot, "bad", now=14)
            self.assertEqual(metrics(db)["pages"], 1)
            release(db, "crossref-window", "worker-a")
            db.close()
            db = connect(path)
            self.assertEqual(acquire(db, "crossref-window", "worker-b", now=15), "cursor-2")
            db.close()

    def test_bad_observation_never_advances_cursor(self):
        with tempfile.TemporaryDirectory() as directory:
            db = connect(Path(directory) / "ledger.sqlite3")
            acquire(db, "scope", "owner", now=10)
            with self.assertRaises(ValueError):
                commit_page(db, "scope", "owner", {"observations": [{"title": "invalid"}]},
                            "lost-cursor", now=11)
            self.assertEqual(metrics(db)["pages"], 0)
            release(db, "scope", "owner")
            self.assertIsNone(acquire(db, "scope", "new-owner", now=12))
            db.close()

    def test_expired_lease_cannot_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            db = connect(Path(directory) / "ledger.sqlite3")
            acquire(db, "scope", "owner", now=10, ttl=2)
            acquire(db, "scope", "new-owner", now=13)
            with self.assertRaises(LeaseBusyError):
                commit_page(db, "scope", "owner", {"observations": []}, None, now=14)
            db.close()


if __name__ == "__main__":
    unittest.main()
