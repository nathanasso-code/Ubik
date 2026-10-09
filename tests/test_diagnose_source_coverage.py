import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("diagnostics", Path(__file__).resolve().parents[1] / "scripts/diagnose_source_coverage.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DiagnosticsTests(unittest.TestCase):
    def test_source_counts_and_failed_feed(self):
        discovery = {"items": [
            {"source_id":"a","url":"https://a.org/1","authors":["Author"],"description":"Abstract"},
            {"source_id":"a","url":"https://a.org/2","authors":[]},
        ], "source_reports":[{"source_id":"a","status":"ok"},{"source_id":"b","status":"error","error":"403"}]}
        relevance = {"items":[{"url":"https://a.org/1","relevance_status":"likely_ai"}]}
        result = module.diagnose(discovery, relevance)
        a, b = result["sources"]
        self.assertEqual((a["feed_named"], a["feed_unspecified"], a["feed_descriptions"]), (1,1,1))
        self.assertEqual((a["likely_ai"], a["unknown"]), (1,1))
        self.assertEqual(b["fetch_status"], "error")
        self.assertEqual(b["stored_items"], 0)
        self.assertEqual(result["purpose"], "coverage_only_not_quality_ranking")

if __name__ == "__main__":
    unittest.main()
