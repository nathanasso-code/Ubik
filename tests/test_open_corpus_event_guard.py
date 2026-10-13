import unittest
from ingestion.open_corpus_event_guard import event_guard,annotate_cards
class EventGuardTests(unittest.TestCase):
    def test_different_sporting_rounds_are_not_same_event(self):
        x=event_guard("Caloundra win round 3 game in Australian soccer", "Caloundra lose round 2 game in Australian soccer")
        self.assertFalse(x["same_event_candidate"])
        self.assertEqual(x["relation_hypothesis"],"related_distinct_events")
    def test_primary_is_not_general_election(self):
        x=event_guard("Mamdani wins New York City mayoral election","Cuomo concedes to Mamdani in Democratic primary election for New York City mayor")
        self.assertFalse(x["same_event_candidate"])
    def test_uncertain_pairs_abstain(self):
        self.assertIsNone(event_guard("Storm hits coast","Storm causes flooding")["same_event_candidate"])
    def test_review_card_keeps_all_sources(self):
        cards=[{"title":"Caloundra round 3","source_titles":["Caloundra win round 3","Caloundra lose round 2"],"source_urls":["a","b"]}]
        result=annotate_cards(cards)
        self.assertTrue(result[0]["same_event_candidate_blocked"])
        self.assertEqual(result[0]["source_urls"],["a","b"])
        self.assertFalse(result[0]["source_independence_verified"])
if __name__=="__main__":unittest.main()
