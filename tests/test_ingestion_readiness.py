import unittest
from pathlib import Path

from ingestion.readiness import readiness


class ReadinessTests(unittest.TestCase):
    def test_report_is_explicitly_not_production_ready(self):
        root = Path(__file__).resolve().parents[1]
        report = readiness(root)
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["network_calls"], 0)
        self.assertEqual(report["deployment_changes"], 0)
        self.assertFalse(report["missing_development_artifacts"])
        self.assertIn("postgres_adapter_not_implemented_or_integration_tested",
                      report["production_blockers"])


if __name__ == "__main__":
    unittest.main()
