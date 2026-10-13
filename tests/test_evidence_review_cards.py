import unittest
from ingestion.epistemic_evidence_gate import fingerprint
from ingestion.evidence_review_cards import build_evidence_cards
class EvidenceReviewCardTests(unittest.TestCase):
    def setUp(self):
        self.a="The energy regulator reported that power demand increased after the plant opened."
        self.b="The city authority reported that power demand stayed unchanged after the plant opened."
        self.sources={"https://a.example/x":{"text":self.a,"sha256":fingerprint(self.a)},
                      "https://b.example/y":{"text":self.b,"sha256":fingerprint(self.b)}}
        self.review={"relation_type":"contradicts_claim","reviewer_id":"editor-1",
                     "left":{"url":"https://a.example/x"},"right":{"url":"https://b.example/y"},
                     "evidence":[{"url":"https://a.example/x","quote":self.a},
                                 {"url":"https://b.example/y","quote":self.b}],
                     "compared_claims":[self.a,self.b],
                     "rationale":"The two statements differ on whether the same electricity demand rose."}
    def test_valid_source_passages_are_not_verified_truth(self):
        result=build_evidence_cards({"reviews":[self.review]},self.sources)
        self.assertEqual(len(result["cards"]),1)
        self.assertEqual(result["cards"][0]["status"],"editorial_review_required")
        self.assertFalse(result["cards"][0]["relation_is_verified"])
        self.assertEqual(result["verified_relations"],0)
        self.assertFalse(result["automatic_publication"])
    def test_fabricated_passage_rejected(self):
        self.review["evidence"][1]["quote"]="This passage was never present in the supplied article body."
        result=build_evidence_cards({"reviews":[self.review]},self.sources)
        self.assertEqual(len(result["cards"]),0)
        self.assertEqual(len(result["rejected"]),1)
if __name__=="__main__":unittest.main()
