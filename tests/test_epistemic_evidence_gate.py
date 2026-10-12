import unittest
from ingestion.epistemic_evidence_gate import validate,fingerprint
class EpistemicEvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.a="The published report says that grid demand rose after the new facility opened."
        self.b="The regulator states that grid demand did not rise after the facility opened."
        self.sources={"https://a.example/x":{"text":self.a,"sha256":fingerprint(self.a)},
                      "https://b.example/y":{"text":self.b,"sha256":fingerprint(self.b)}}
        self.review={"relation_type":"contradicts_claim","reviewer_id":"editor-1",
                     "left":{"url":"https://a.example/x"},"right":{"url":"https://b.example/y"},
                     "evidence":[{"url":"https://a.example/x","quote":self.a},
                                 {"url":"https://b.example/y","quote":self.b}],
                     "compared_claims":[self.a,self.b],
                     "rationale":"The two sources make explicitly opposite statements about demand change."}
    def test_valid_quotes_only_enable_review_not_publication(self):
        result=validate(self.review,self.sources)
        self.assertTrue(result["eligible_for_editorial_review"],result["errors"])
        self.assertFalse(result["automatic_publication"])
        self.assertFalse(result["verified_as_true"])
    def test_missing_opposite_source_blocks_contradiction(self):
        self.review["evidence"]=self.review["evidence"][:1]
        self.assertFalse(validate(self.review,self.sources)["eligible_for_editorial_review"])
    def test_hallucinated_quote_blocks(self):
        self.review["evidence"][1]["quote"]="A fabricated sentence not present in the article body."
        self.assertIn("evidence_1_quote_not_found_verbatim",validate(self.review,self.sources)["errors"])
    def test_tampered_source_hash_blocks(self):
        self.sources["https://b.example/y"]["sha256"]="tampered"
        self.assertFalse(validate(self.review,self.sources)["eligible_for_editorial_review"])
    def test_claim_without_reviewer_blocks(self):
        self.review["reviewer_id"]=""
        self.assertFalse(validate(self.review,self.sources)["eligible_for_editorial_review"])
if __name__=="__main__":unittest.main()
