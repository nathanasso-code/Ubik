import unittest
from ingestion.discovery_acquisition_gap_audit import audit, canonical

class GapAuditTests(unittest.TestCase):
    def test_normalize_tracking(self):
        self.assertEqual(canonical("https://EXAMPLE.org/story/?utm_source=x&id=3"), "https://example.org/story?id=3")
    def test_separate_missing_and_short(self):
        discovered={"items":[{"url":"https://example.org/a"},{"url":"https://example.org/a?utm_source=x"},{"url":"https://example.org/b"},{"url":"https://example.org/c"}]}
        acquired={"documents":[{"url":"https://example.org/a","text":"x"*850},{"url":"https://example.org/b","description":"short"}]}
        out=audit(discovered,acquired)
        self.assertEqual(out["discovery"]["unique_urls"],3)
        self.assertEqual(out["discovery"]["duplicate_observations"],1)
        self.assertEqual(out["acquisition"]["discovered_urls_with_800plus_chars"],1)
        self.assertEqual(out["acquisition"]["discovered_urls_with_short_text"],1)
        self.assertEqual(out["acquisition"]["discovered_urls_without_acquired_record"],1)
    def test_empty(self):
        self.assertIsNone(audit({"items":[]},{})["acquisition"]["substantial_fraction_of_discovered"])

if __name__=="__main__":
    unittest.main()
