import unittest
from ingestion.cross_source_llm_adjudication import evaluate,passages
class GroundingTests(unittest.TestCase):
    def test_existing_passage_ids(self):
        a=[{"id":"A1","text":"A real article paragraph"}]
        b=[{"id":"B1","text":"Another real article paragraph"}]
        proposal={"relation":"same_event","evidence_a_id":"A1","evidence_b_id":"B1"}
        x=evaluate(proposal,a,b)
        self.assertTrue(x["accepted_for_review"])
        self.assertTrue(x["evidence_a_valid"])
        self.assertTrue(x["evidence_b_valid"])
    def test_hallucinated_passage_id_rejected(self):
        x=evaluate({"relation":"same_event","evidence_a_id":"A900","evidence_b_id":"B1"},
          [{"id":"A1","text":"Real"}],[{"id":"B1","text":"Real"}])
        self.assertFalse(x["accepted_for_review"])
        self.assertFalse(x["evidence_a_valid"])
        self.assertTrue(x["evidence_b_valid"])
    def test_passage_segmentation(self):
        p=passages("This is a sufficiently long paragraph describing the incident in some detail.\n\nThis is another sufficiently long paragraph about the incident.","A")
        self.assertEqual([x["id"] for x in p],["A1","A2"])
if __name__=="__main__":unittest.main()
