import unittest

from ingestion.ubik_v6_editorial import controls, proper_names, repair


def setup(facts_by_item, origins):
    schede = {i: {"item_id": i, "facts": fs, "theses": []} for i, fs in facts_by_item.items()}
    items = {i: {"item_id": i, "origin": origins[i], "title": "", "text": " ".join(f["statement"] for f in fs)}
             for i, fs in facts_by_item.items()}
    return schede, items


def page(fact_items, statement="X"):
    return {"facts": [{"id": "F1", "statement": statement, "items": fact_items}], "comments": [], "analyses": [], "excluded": []}


class Independence(unittest.TestCase):
    def test_sources_inside_one_outlet_count_once(self):
        schede, items = setup({"a": [{"id": "f1", "statement": "s", "according_to": "op-ed"},
                                     {"id": "f2", "statement": "s", "according_to": "spokesperson"}]}, {"a": "ars"})
        p = page([{"item_id": "a", "fact_ref": "f1"}, {"item_id": "a", "fact_ref": "f2"}])
        controls(p, schede, items)
        self.assertEqual(p["facts"][0]["independent_count"], 1)
        self.assertEqual(p["facts"][0]["bundled_note_facts"], 2)

    def test_two_outlets_own_reporting_count_twice(self):
        schede, items = setup({"a": [{"id": "f1", "statement": "s", "according_to": "own reporting"}],
                               "b": [{"id": "f1", "statement": "s", "according_to": "own reporting"}]}, {"a": "x", "b": "y"})
        p = page([{"item_id": "a", "fact_ref": "f1"}, {"item_id": "b", "fact_ref": "f1"}])
        controls(p, schede, items)
        self.assertEqual(p["facts"][0]["independent_count"], 2)

    def test_outlets_relaying_the_same_original_collapse(self):
        schede, items = setup({"a": [{"id": "f1", "statement": "s", "according_to": "Sveriges Radio"}],
                               "b": [{"id": "f1", "statement": "s", "according_to": "sveriges radio"}]}, {"a": "x", "b": "y"})
        p = page([{"item_id": "a", "fact_ref": "f1"}, {"item_id": "b", "fact_ref": "f1"}])
        controls(p, schede, items)
        self.assertEqual(p["facts"][0]["independent_count"], 1)

    def test_outlet_citing_another_outlet_collapses(self):
        schede, items = setup({"a": [{"id": "f1", "statement": "s", "according_to": "own reporting"}],
                               "b": [{"id": "f1", "statement": "s", "according_to": "The Guardian"}]},
                              {"a": "guardian-ai", "b": "netzpolitik"})
        p = page([{"item_id": "a", "fact_ref": "f1"}, {"item_id": "b", "fact_ref": "f1"}])
        controls(p, schede, items)
        self.assertEqual(p["facts"][0]["independent_count"], 1)


class Mismatch(unittest.TestCase):
    def test_reference_without_shared_names_is_removed(self):
        schede, items = setup({"n": [{"id": "f1", "statement": "The German government and Nvidia agreed to cooperate."}]}, {"n": "netzpolitik"})
        p = page([{"item_id": "n", "fact_ref": "f1"}], "Un rapporto di Spotlight on Corruption ha rilevato che il governo britannico")
        log = repair(p, schede, items)
        self.assertTrue(any(r.get("removed") == "fact_source_mismatch" for r in log))
        self.assertEqual(p["facts"], [])

    def test_translated_names_match_by_prefix(self):
        schede, items = setup({"t": [{"id": "f1", "statement": "The European Parliament debated and the Commission defended."}]}, {"t": "tpp"})
        p = page([{"item_id": "t", "fact_ref": "f1"}], "Il Parlamento europeo ha discusso e la Commissione ha difeso")
        repair(p, schede, items)
        self.assertEqual(len(p["facts"]), 1)

    def test_proper_names_skip_first_word(self):
        self.assertEqual(proper_names("Il Texas ha citato OpenAI"), {"texas", "opena"})


if __name__ == "__main__":
    unittest.main()
