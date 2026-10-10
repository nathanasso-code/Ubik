import tempfile
import unittest
from pathlib import Path

from ingestion.archive import archive_snapshot
from ingestion.payload_codec import canonical_payload
from ingestion.sqlite_ledger import acquire, commit_page, connect


class CanonicalPayloadTests(unittest.TestCase):
    def test_file_and_sqlite_hash_identical(self):
        snapshot = {"connector": "crossref", "observations": [
            {"connector": "crossref", "source_id": "crossref-works",
             "external_id": "10.1234/cafe", "title": "Café"}]}
        payload, digest = canonical_payload(snapshot)
        with tempfile.TemporaryDirectory() as directory:
            file = archive_snapshot(snapshot, Path(directory) / "archives")
            self.assertEqual(file["sha256"], digest)
            self.assertEqual(Path(file["path"]).read_bytes(), payload + bytes([10]))
            db = connect(Path(directory) / "ledger.sqlite3")
            acquire(db, "scope", "owner", now=10)
            stored = commit_page(db, "scope", "owner", snapshot, None, now=11)
            self.assertEqual(stored["sha256"], digest)
            db.close()

    def test_nonfinite_numbers_are_rejected(self):
        with self.assertRaises(ValueError):
            canonical_payload({"observations": [], "bad": float("nan")})


if __name__ == "__main__":
    unittest.main()
