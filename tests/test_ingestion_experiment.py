import tempfile
import unittest
from pathlib import Path
from ingestion.experiment_plan import validate_plan
from ingestion.experiment import run_experiment


class ExperimentTests(unittest.TestCase):
    def test_plan_limits_and_duplicate_sources(self):
        plan = {"sources": [{"provider": "bluesky", "source": "example.bsky.social"}]}
        self.assertEqual(validate_plan(plan)[0]["max_pages"], 2)
        with self.assertRaises(ValueError):
            validate_plan({"sources": plan["sources"] * 2})
        with self.assertRaises(ValueError):
            validate_plan({"sources": [{"provider": "mastodon", "source": "localhost"}]})
        with self.assertRaises(ValueError):
            validate_plan({"sources": [{"provider": "crossref", "source": "crossref-works"}]})

    def test_dry_run_makes_no_network_calls(self):
        def unexpected(*args, **kwargs):
            raise AssertionError("Network runner invoked")
        report = run_experiment({"sources": [{"provider": "bluesky",
                                               "source": "example.bsky.social"}]},
                                archive_dir="/nonexistent", checkpoint_dir="/nonexistent",
                                runner=unexpected)
        self.assertEqual(report["network_calls"], 0)
        self.assertEqual(report["maximum_page_requests"], 2)

    def test_isolates_provider_failure(self):
        def fake(provider, **kwargs):
            if provider == "mastodon":
                raise OSError("provider unavailable")
            return {"pages": 1, "observations": 1}
        plan = {"sources": [
            {"provider": "mastodon", "source": "example.social"},
            {"provider": "bluesky", "source": "example.bsky.social"}]}
        with tempfile.TemporaryDirectory() as directory:
            report = run_experiment(plan, archive_dir=Path(directory) / "archives",
                                    checkpoint_dir=Path(directory) / "checkpoints",
                                    live=True, runner=fake)
            self.assertEqual(report["status"], "finished_with_errors")
            self.assertEqual([x["status"] for x in report["sources"]], ["error", "ok"])


if __name__ == "__main__":
    unittest.main()
