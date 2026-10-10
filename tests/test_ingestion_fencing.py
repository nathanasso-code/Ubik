import tempfile
import unittest
from pathlib import Path

from ingestion.sqlite_ledger import LeaseBusyError, acquire, commit_page, connect, release


class FencingTests(unittest.TestCase):
    def test_stale_epoch_rejected_even_if_owner_string_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            db = connect(Path(directory) / "ledger.sqlite3")
            acquire(db, "scope", "same-owner", now=10, ttl=2)
            epoch1 = db.execute("SELECT lease_epoch FROM ingestion_scopes").fetchone()[0]
            release(db, "scope", "same-owner")
            acquire(db, "scope", "same-owner", now=11, ttl=10)
            epoch2 = db.execute("SELECT lease_epoch FROM ingestion_scopes").fetchone()[0]
            self.assertGreater(epoch2, epoch1)
            with self.assertRaises(LeaseBusyError):
                commit_page(db, "scope", "same-owner", {"observations": []},
                            "bad-cursor", now=12, epoch=epoch1)
            saved = commit_page(db, "scope", "same-owner", {"observations": []},
                                "valid-cursor", now=12, epoch=epoch2)
            self.assertTrue(saved["new_page"])
            self.assertEqual(db.execute("SELECT cursor FROM ingestion_scopes").fetchone()[0],
                             "valid-cursor")
            db.close()


if __name__ == "__main__":
    unittest.main()
