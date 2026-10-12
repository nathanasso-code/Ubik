"""Offline tests for the opt-in Mastodon discovery pilot."""
import unittest

from ingestion.mastodon_discovery import collect, discovery_url


class MastodonDiscoveryTests(unittest.TestCase):
    def test_modes(self):
        self.assertIn("local=true", discovery_url("mastodon.social", "local"))
        self.assertIn("remote=true", discovery_url("mastodon.social", "federated"))
        self.assertIn("/tag/science?", discovery_url("mastodon.social", "tag", tag="science"))
        self.assertIn("/accounts/123/statuses?", discovery_url("mastodon.social", "account", account_id="123"))

    def test_reject_invalid(self):
        for host in ("localhost", "127.0.0.1", "http://mastodon.social"):
            with self.assertRaises(ValueError):
                discovery_url(host)
        with self.assertRaises(ValueError):
            discovery_url("mastodon.social", "tag", tag="a/b")

    def test_public_only_and_stable_uri(self):
        base = {"id": "123", "visibility": "public", "reblog": None,
                "url": "https://example.social/@alice/123",
                "uri": "https://example.social/users/alice/statuses/123",
                "account": {"url": "https://example.social/@alice"},
                "created_at": "2026-10-12T00:00:00Z", "tags": [{"name": "science"}]}
        private = dict(base, visibility="private")
        boosted = dict(base, reblog={"id": "another"})
        result = collect("mastodon.social", "tag", tag="science",
                         fetch=lambda url: [base, private, boosted])
        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(result["next_max_id"], "123")
        self.assertEqual(result["observations"][0]["external_id"], base["uri"])
        self.assertEqual(result["observations"][0]["metadata"]["tags"], ["science"])


if __name__ == "__main__":
    unittest.main()
