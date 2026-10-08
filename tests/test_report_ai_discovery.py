import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("report", Path(__file__).resolve().parents[1] / "scripts/report_ai_discovery.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

class ReportTests(unittest.TestCase):
    def test_report(self):
        text = report.report({"retrieved_at":"2026-10-08T10:00:00Z", "coverage":{"successful_feeds":1, "failed_feeds":1}, "source_reports":[{"source_id":"personal-blog", "status":"ok", "seen":3, "new":2, "with_named_author":3, "missing_named_author":0}]})
        self.assertIn("personal-blog", text)
        self.assertIn("successful_feeds: 1", text)
        self.assertIn("With author", text)
        self.assertIn("not completeness", text)

if __name__ == "__main__":
    unittest.main()
