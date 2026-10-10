import tempfile
import unittest
from pathlib import Path

from ingestion.experiment import run_experiment
from ingestion.sqlite_ledger import connect


class SQLiteExperimentTests(unittest.TestCase):
    def test_live_experiment_uses_transactional_ledger_and_reports_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = connect(root / "ledger.sqlite3")
            plan = {"sources": [{"provider": "crossref", "source": "crossref-works",
                                "from_date": "2026-10-09", "to_date": "2026-10-10",
                                "max_pages": 1, "page_size": 2}]}
            def runner(provider, **kwargs):
                self.assertIs(kwargs["ledger"], db)
                return {"provider": provider, "status": "completed", "pages": 0}
            result = run_experiment(plan, archive_dir=root / "archives",
                                    checkpoint_dir=root / "checkpoints",
                                    live=True, runner=runner, ledger=db)
            self.assertEqual(result["status"], "finished")
            self.assertEqual(result["coverage"]["storage"], "sqlite")
            self.assertTrue(result["coverage"]["integrity"]["integrity_ok"])
            self.assertEqual(result["coverage"]["metrics"]["pages"], 0)
            db.close()


if __name__ == "__main__":
    unittest.main()
