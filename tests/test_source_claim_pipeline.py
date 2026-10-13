import unittest
from ingestion.epistemic_evidence_gate import fingerprint
from ingestion.source_claim_candidates import claim_candidates
from ingestion.source_claim_comparisons import compare_candidates
class ClaimPipelineTests(unittest.TestCase):
    def test_end_to_end_candidate_and_comparison_without_verdict(self):
        a="The energy regulator reported that grid consumption increased after the plant opened."
        b="The city authority reported that grid consumption stayed unchanged after the plant opened."
        sources={"https://a.example/x":{"text":a,"sha256":fingerprint(a)},
                 "https://b.example/y":{"text":b,"sha256":fingerprint(b)}}
        extracted=claim_candidates(sources)
        self.assertEqual(sum(len(s["candidates"]) for s in extracted["sources"]),2)
        review={"selected":[{"frozen_rank":7,"left":{"url":"https://a.example/x","title":"Report A"},
                             "right":{"url":"https://b.example/y","title":"Report B"}}]}
        result=compare_candidates(review,extracted)
        self.assertEqual(len(result["comparisons"]),1)
        self.assertEqual(result["comparisons"][0]["relation_type"],"insufficient_evidence")
        self.assertFalse(result["published"])
        self.assertFalse(result["comparisons"][0]["verified"])
    def test_changed_hash_excludes_claims(self):
        r=claim_candidates({"https://a.example/x":{"text":"A valid sentence long enough to be a candidate for review.","sha256":"wrong"}})
        self.assertEqual(r["sources"][0]["candidates"],[])
if __name__=="__main__":unittest.main()
