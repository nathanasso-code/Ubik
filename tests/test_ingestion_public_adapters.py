import unittest
from ingestion.public_adapters import (bluesky_collect, bluesky_url, mastodon_collect,
                                       mastodon_url, openalex_collect, openalex_url, crossref_collect, crossref_url)


class PublicAdaptersTests(unittest.TestCase):
    def test_bluesky_actor_feed_and_provenance(self):
        result = bluesky_collect("example.bsky.social", fetch=lambda _: {"feed": [
            {"post": {"uri": "at://did:plc:abc/app.bsky.feed.post/xyz",
                      "author": {"did": "did:plc:abc"},
                      "record": {"text": "Hello from Bluesky", "createdAt": "2026-10-10T00:00:00Z"}}}
        ], "cursor": "next"})
        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["observations"][0]["validation"], "not_assessed")
        self.assertEqual(result["next_cursor"], "next")
        self.assertIn("actor=example.bsky.social", bluesky_url("example.bsky.social"))
        with self.assertRaises(ValueError):
            bluesky_url("bad/actor")

    def test_mastodon_only_public_non_boosts(self):
        statuses = [
            {"id": "1", "visibility": "public", "url": "https://example.social/@alice/1",
             "account": {"url": "https://example.social/@alice"}, "created_at": "2026-10-10T00:00:00Z",
             "content": "<p>Content not stored</p>", "reblog": None},
            {"id": "2", "visibility": "private", "url": "https://example.social/@alice/2",
             "account": {"url": "https://example.social/@alice"}},
        ]
        result = mastodon_collect("example.social", fetch=lambda _: statuses)
        self.assertEqual(len(result["observations"]), 1)
        self.assertNotIn("Content not stored", str(result))
        self.assertEqual(result["next_max_id"], "2")
        self.assertIn("local=true", mastodon_url("example.social"))
        with self.assertRaises(ValueError):
            mastodon_url("http://example.social")
        with self.assertRaises(ValueError):
            mastodon_url("localhost")
        with self.assertRaises(ValueError):
            mastodon_url("127.0.0.1")

    def test_crossref_metadata_only(self):
        result = crossref_collect("2026-10-01", "2026-10-10", fetch=lambda _: {
            "message": {"items": [{"DOI": "10.1000/test", "title": ["Research article"],
                                   "publisher": "Example"}], "next-cursor": "next"}})
        self.assertEqual(result["observations"][0]["url"], "https://doi.org/10.1000/test")
        self.assertEqual(result["next_cursor"], "next")
        self.assertEqual(result["observations"][0]["validation"], "not_assessed")
        with self.assertRaises(ValueError):
            crossref_url("2026-10-10", "2026-10-01")

    def test_openalex_date_window_and_cursor(self):
        result = openalex_collect("2026-10-01", "2026-10-10", fetch=lambda _: {
            "results": [{"id": "https://openalex.org/W123", "display_name": "A research paper",
                         "doi": "https://doi.org/10.1000/xyz", "publication_date": "2026-10-09"}],
            "meta": {"next_cursor": "abc"}})
        self.assertEqual(result["next_cursor"], "abc")
        self.assertEqual(result["observations"][0]["metadata"]["openalex_id"], "https://openalex.org/W123")
        self.assertIn("from_publication_date", openalex_url("2026-10-01", "2026-10-10"))
        with self.assertRaises(ValueError):
            openalex_url("2026-10-10", "2026-10-01")


if __name__ == "__main__":
    unittest.main()
