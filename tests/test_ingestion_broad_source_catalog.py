import csv
import io
import unittest
from ingestion.broad_source_catalog import build, to_csv


class BroadSourceCatalogTests(unittest.TestCase):
    def test_retains_old_undated_and_non_ai_sources(self):
        discovery = {"items": [
            {"url": "https://example.org/old", "title": "Ancient mathematics",
             "source_id": "a", "published_raw": "2020-01-01"},
            {"url": "https://example.org/new", "title": "Language model research",
             "source_id": "b", "description": "Language model results"},
            {"url": "https://example.org/old", "title": "Ancient mathematics",
             "source_id": "c", "description": "Additional description"},
            {"url": "", "title": "Missing URL", "source_id": "d"}]}
        result = build(discovery)
        self.assertEqual(result["documents"], 2)
        self.assertEqual(result["invalid_records"], 1)
        self.assertEqual(result["editorially_excluded"], 0)
        old = next(x for x in result["items"] if x["url"].endswith("old"))
        self.assertEqual(old["source_ids"], ["a", "c"])
        self.assertEqual(old["relevance_hint"], "needs_topic_review")
        self.assertTrue(all(x["review_status"] == "unreviewed" for x in result["items"]))
        self.assertEqual(len(list(csv.DictReader(io.StringIO(to_csv(result))))), 2)


if __name__ == "__main__":
    unittest.main()
