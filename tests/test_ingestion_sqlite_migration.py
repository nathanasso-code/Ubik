import sqlite3
import tempfile
import unittest
from pathlib import Path

from ingestion.sqlite_ledger import acquire, connect


class LeaseMigrationTests(unittest.TestCase):
    def test_existing_scope_table_gains_epoch_without_losing_cursor(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.sqlite3"
            db = sqlite3.connect(path)
            db.execute("""CREATE TABLE ingestion_scopes (
                scope_key TEXT PRIMARY KEY, cursor TEXT, archive_sha256 TEXT,
                lease_owner TEXT, lease_until REAL NOT NULL DEFAULT 0)""")
            db.execute("INSERT INTO ingestion_scopes(scope_key, cursor) VALUES (?, ?)",
                       ("scope", "resume-cursor"))
            db.commit()
            db.close()
            ledger = connect(path)
            self.assertEqual(acquire(ledger, "scope", "worker", now=10), "resume-cursor")
            epoch = ledger.execute("SELECT lease_epoch FROM ingestion_scopes WHERE scope_key=?",
                                   ("scope",)).fetchone()[0]
            self.assertEqual(epoch, 1)
            ledger.close()


if __name__ == "__main__":
    unittest.main()
