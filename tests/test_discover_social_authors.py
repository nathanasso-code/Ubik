import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("social", Path(__file__).resolve().parents[1] / "scripts/discover_social_authors.py")
social = importlib.util.module_from_spec(spec)
spec.loader.exec_module(social)

class SocialTests(unittest.TestCase):
    @patch.object(social, "fetch", return_value={"actors": [{"handle":"test.bsky.social","displayName":"Test"}]})
    def test_bluesky(self, fetch):
        result = social.bluesky_candidates("AI")
        self.assertEqual(result[0]["identity_status"], "unverified")
        self.assertEqual(result[0]["profile_url"], "https://bsky.app/profile/test.bsky.social")
    @patch.object(social, "fetch", return_value={"accounts": [{"acct":"someone","url":"https://mastodon.social/@someone","note":"<p>Researcher</p>"}]})
    def test_mastodon(self, fetch):
        result = social.mastodon_candidates("https://mastodon.social", "AI")
        self.assertEqual(result[0]["description"], "Researcher")
    def test_reject_insecure_instance(self):
        with self.assertRaises(ValueError):
            social.mastodon_candidates("http://example.org", "AI")
    @patch.object(social, "mastodon_candidates", side_effect=Exception("blocked"))
    @patch.object(social, "bluesky_candidates", return_value=[])
    def test_partial_failure(self, *_):
        result = social.discover(["AI"], ["https://mastodon.social"])
        self.assertEqual(len(result["errors"]), 1)

if __name__ == "__main__":
    unittest.main()
