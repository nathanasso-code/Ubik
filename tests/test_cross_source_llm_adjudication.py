import unittest
from ingestion.cross_source_llm_adjudication import evaluate
class GroundingTests(unittest.TestCase):
    def test_grounded_quotes(self):
        a="The coastal storm forced residents to leave their homes in the northern town."
        b="Residents evacuated the northern town as the coastal storm approached overnight."
        proposal={"relation":"same_event","quote_a":"coastal storm forced residents","quote_b":"coastal storm approached overnight"}
        x=evaluate(proposal,a,b)
        self.assertTrue(x["accepted_for_review"])
        self.assertTrue(x["quote_a_valid"])
        self.assertTrue(x["quote_b_valid"])
    def test_missing_quote_rejected(self):
        x=evaluate({"relation":"same_event","quote_a":"invented description of storm","quote_b":"coastal storm approached overnight"},
          "The coastal storm forced residents to leave their homes.",
          "Residents evacuated as the coastal storm approached overnight.")
        self.assertFalse(x["accepted_for_review"])
        self.assertFalse(x["quote_a_valid"])
        self.assertTrue(x["quote_b_valid"])
if __name__=="__main__":unittest.main()
