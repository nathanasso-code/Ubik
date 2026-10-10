import tempfile
import unittest
from pathlib import Path

from ingestion.audit_sqlite import audit_ledger
from ingestion.sqlite_ledger import acquire, commit_page, connect, release


class LedgerAuditTests(unittest.TestCase):
    def test_integrity_audit_and_detects_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            db = connect(Path(directory) / "ledger.sqlite3")
            acquire(db, "scope", "worker", now=10)
            snapshot = {"connector": "openalex", "observations": [
                {"connector": "openalex", "source_id": "openalex-works",
                 "external_id": "https://openalex.org/W1"}]}
            saved = commit_page(db, "scope", "worker", snapshot, None, now=11)
            self.assertTrue(audit_ledger(db)["integrity_ok"])
            db.execute("UPDATE ingestion_observations SET external_id=? WHERE page_id=?",
                       ("changed", saved["page_id"]))
            result = audit_ledger(db)
            self.assertFalse(result["integrity_ok"])
            self.assertEqual(len(result["invalid_pages"]), 1)
            db.close()


if __name__ == "__main__":
    unittest.main()
