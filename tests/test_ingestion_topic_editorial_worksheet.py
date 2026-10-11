import csv
import io
import unittest
from ingestion.topic_editorial_worksheet import worksheet, render_csv


class TopicEditorialWorksheetTests(unittest.TestCase):
    def test_sample_across_uncertainty_strata_and_no_fabricated_decisions(self):
        items = []
        for i in range(45):
            reasons = (["possible_same_event_pair"] if i == 0 else
                       ["missing_substantive_description"] if i == 1 else
                       ["no_specific_area"] if i < 9 else ["routine_content_review"])
            items.append({"url": f"https://example.org/{i}", "title": f"Paper {i}",
                          "source_ids": [f"source-{i % 4}"], "review_reasons": reasons,
                          "description_evidence": [f"Source evidence {i}."]})
        rows = worksheet({"items": items}, limit=30)
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({row["url"] for row in rows}), 30)
        self.assertTrue(any("possible_same_event_pair" in x["review_reasons"] for x in rows))
        self.assertTrue(any("missing_substantive_description" in x["review_reasons"] for x in rows))
        self.assertTrue(any("routine_content_review" in x["review_reasons"] for x in rows))
        self.assertTrue(all(x["feed_decision"] == "" and x["central_message"] == "" for x in rows))
        parsed = list(csv.DictReader(io.StringIO(render_csv(rows))))
        self.assertEqual(len(parsed), 30)

    def test_no_empty_source_crash(self):
        rows = worksheet({"items": [{"url": "https://example.org/1",
                                     "source_ids": [], "review_reasons": []}]})
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
