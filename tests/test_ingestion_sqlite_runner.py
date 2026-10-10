import tempfile
import unittest
from pathlib import Path

from ingestion.run_batch import run_pages
from ingestion.sqlite_ledger import LeaseBusyError, connect, metrics


class SQLiteRunnerIntegrationTests(unittest.TestCase):
    def test_resume_across_database_connections(self):
        calls = []
        def fetch(_actor, *, limit, cursor):
            calls.append(cursor)
            return {"connector": "bluesky", "observations": [
                {"connector": "bluesky", "source_id": "did:plc:example",
                 "external_id": "at://did:plc:example/post/" + str(len(calls)),
                 "url": "https://bsky.app/profile/example/post/1"}],
                "next_cursor": "page-two" if cursor is None else None}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_path = root / "ledger.sqlite3"
            db = connect(db_path)
            opts = dict(source="example.bsky.social", archive_dir=root / "unused",
                        checkpoint_dir=root / "unused-checkpoints",
                        max_pages=1, fetchers={"bluesky": fetch},
                        sleep=lambda _: None)
            first = run_pages("bluesky", ledger=db, **opts)
            self.assertEqual(first["status"], "budget_exhausted")
            db.close()
            db = connect(db_path)
            second = run_pages("bluesky", ledger=db, **opts)
            self.assertEqual(second["status"], "completed")
            self.assertEqual(calls, [None, "page-two"])
            self.assertEqual(metrics(db)["pages"], 2)
            self.assertEqual(metrics(db)["observations"], 2)
            self.assertFalse((root / "unused-checkpoints").exists())
            db.close()

    def test_scientific_empty_normalized_page_resumes_by_cursor(self):
        calls = []
        def fetch(_from, _to, *, rows, cursor):
            calls.append(cursor)
            return {"connector": "crossref", "observations": [],
                    "next_cursor": "provider-continues", "invalid": 0}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = connect(root / "ledger.sqlite3")
            opts = dict(source="crossref-works", archive_dir=root / "a",
                        checkpoint_dir=root / "c", max_pages=1, page_size=5,
                        from_date="2026-10-09", to_date="2026-10-10",
                        ledger=db, fetchers={"crossref": fetch})
            first = run_pages("crossref", **opts)
            self.assertEqual(first["status"], "budget_exhausted")
            second = run_pages("crossref", **opts)
            self.assertEqual(second["pages"], 1)
            self.assertEqual(calls, ["*", "provider-continues"])
            db.close()

    def test_second_database_connection_cannot_fetch_same_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_path = root / "ledger.sqlite3"
            first_db, second_db = connect(db_path), connect(db_path)
            nested_calls = []
            def other_fetch(*_args, **_kwargs):
                nested_calls.append("unexpected")
                raise AssertionError("Must never fetch while leased")
            def first_fetch(*_args, **_kwargs):
                with self.assertRaises(LeaseBusyError):
                    run_pages("bluesky", source="example.bsky.social",
                              archive_dir=root / "a", checkpoint_dir=root / "c",
                              ledger=second_db, max_pages=1,
                              fetchers={"bluesky": other_fetch})
                return {"connector": "bluesky", "observations": [],
                        "next_cursor": None}
            run_pages("bluesky", source="example.bsky.social",
                      archive_dir=root / "a", checkpoint_dir=root / "c",
                      ledger=first_db, max_pages=1,
                      fetchers={"bluesky": first_fetch})
            self.assertEqual(nested_calls, [])
            first_db.close()
            second_db.close()

    def test_failure_releases_lease_and_keeps_cursor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = connect(root / "ledger.sqlite3")
            def fail(*_args, **_kwargs):
                raise OSError("network failure")
            opts = dict(source="example.bsky.social", archive_dir=root / "a",
                        checkpoint_dir=root / "c", max_pages=1, ledger=db)
            with self.assertRaises(OSError):
                run_pages("bluesky", fetchers={"bluesky": fail}, **opts)
            self.assertEqual(metrics(db)["pages"], 0)
            def success(*_args, **_kwargs):
                return {"connector": "bluesky", "observations": [],
                        "next_cursor": None}
            result = run_pages("bluesky", fetchers={"bluesky": success}, **opts)
            self.assertEqual(result["pages"], 1)
            db.close()


if __name__ == "__main__":
    unittest.main()
