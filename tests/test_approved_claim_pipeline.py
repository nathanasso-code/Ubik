import unittest
from ingestion.approved_claim_pipeline import run
class ApprovedClaimPipelineTests(unittest.TestCase):
    def test_acquisition_to_claims_keeps_unverified_status(self):
        html="<article><p>The regulator measured electricity consumption after the data center opened.</p><p>The municipality separately reported the construction schedule for the facility.</p></article>"
        result=run("https://example.org/a",{"approved_hosts":["example.org"]},
                   fetch=lambda url,policy:{"html":html,"retrieved_at_utc":"2026-10-13T00:00:00Z","robots_checked":True,"rights_confirmed_by_operator":True})
        self.assertEqual(len(result["sources"]),1)
        self.assertGreater(len(result["claims"]["sources"][0]["candidates"]),0)
        self.assertEqual(result["verified_claims"],0)
        self.assertFalse(result["published"])
if __name__=="__main__":unittest.main()
