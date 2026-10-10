import tempfile
import unittest
from pathlib import Path

from ingestion.run_batch import run_pages


class BatchPaginationEdgesTests(unittest.TestCase):
    def test_crossref_short_page_is_terminal_even_with_cursor(self):
        calls = []
        def crossref(from_date, to_date, *, rows, cursor):
            calls.append(cursor)
            return {"connector": "crossref", "observations": [
                {"connector": "crossref", "source_id": "crossref-works",
                 "external_id": "10.1234/example", "url": "https://doi.org/10.1234/example"}],
                "next_cursor": "provider-next"}
        with tempfile.TemporaryDirectory() as directory:
            result = run_pages("crossref", source="crossref-works",
                               from_date="2026-10-09", to_date="2026-10-10",
                               archive_dir=Path(directory) / "a",
                               checkpoint_dir=Path(directory) / "c",
                               max_pages=3, page_size=5,
                               fetchers={"crossref": crossref}, sleep=lambda _: None)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(calls, ["*"])

    def test_empty_page_with_cursor_continues_until_cursor_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_pages("openalex", source="openalex-works",
                               from_date="2026-10-09", to_date="2026-10-10",
                               archive_dir=Path(directory) / "a",
                               checkpoint_dir=Path(directory) / "c",
                               fetchers={"openalex": lambda *_args, **_kwargs: {
                                   "connector": "openalex", "observations": [],
                                   "next_cursor": "next"}},
                               sleep=lambda _: None)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["pages"], 2)


if __name__ == "__main__":
    unittest.main()
