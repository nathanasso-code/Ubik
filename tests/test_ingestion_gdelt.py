import unittest
from ingestion.contracts import observation, canonical_url_hint
from ingestion.gdelt_doc import request_url, parse_response, collect


class IngestionContractTests(unittest.TestCase):
    def test_no_editorial_decision(self):
        x = observation(connector="test", source_id="publisher", external_id="1",
                        title="Story", url="https://example.org/news?utm_source=rss&id=1",
                        discovered_from="https://example.org/feed")
        self.assertEqual(x["editorial_selection"], "not_assessed")
        self.assertEqual(x["event_identity"], "not_assessed")
        self.assertEqual(x["canonical_url_hint"], "https://example.org/news?id=1")

    def test_reject_non_http_url(self):
        with self.assertRaises(ValueError):
            canonical_url_hint("file:///etc/passwd")


class GdeltAdapterTests(unittest.TestCase):
    def test_request_is_bounded(self):
        with self.assertRaises(ValueError):
            request_url("news", maxrecords=251)
        self.assertIn("mode=artlist", request_url("climate change", timespan="1h"))

    def test_metadata_only_and_truncation(self):
        payload = {"articles": [
            {"url": "https://publisher.example/story", "title": "A",
             "seendate": "20261010120000", "language": "English", "domain": "publisher.example"},
            {"url": "javascript:alert(1)", "title": "Bad"},
        ]}
        result = parse_response(payload, query="climate", timespan="1h", maxrecords=2)
        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["invalid_indices"], [1])
        self.assertTrue(result["potentially_truncated"])
        self.assertEqual(result["observations"][0]["metadata"]["time_basis"],
                         "gdelt_seen_date_not_original_publication")

    def test_injected_fetch(self):
        result = collect("science", fetch=lambda _: {"articles": []})
        self.assertEqual(result["observations"], [])
        self.assertFalse(result["potentially_truncated"])


if __name__ == "__main__":
    unittest.main()
