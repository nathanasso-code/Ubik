import csv,tempfile,unittest
from pathlib import Path
from ingestion.nli_independent_review import export,adjudicate,FIELDS
class ReviewTests(unittest.TestCase):
 def test_two_reviewers_agree(self):
  packet={"items":[{"item_id":"abc","url_a":"a","url_b":"b","statement_index":0,"statement_a":"one","statement_b":"two"}]}
  with tempfile.TemporaryDirectory() as d:
   a,b=Path(d)/"a.csv",Path(d)/"b.csv"
   export(packet,a);export(packet,b)
   for p in (a,b):
    with p.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    rows[0].update(event_identity="same_event",statement_relation="equivalent",evidence_sufficient="yes")
    with p.open("w",newline="",encoding="utf-8") as f:
     w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
   self.assertEqual(adjudicate(packet,a,b)["coverage"]["agreed"],1)
 def test_unannotated_is_not_gold(self):
  packet={"items":[{"item_id":"abc","url_a":"a","url_b":"b","statement_index":0}]}
  with tempfile.TemporaryDirectory() as d:
   a,b=Path(d)/"a.csv",Path(d)/"b.csv"
   export(packet,a);export(packet,b)
   with self.assertRaises(ValueError):adjudicate(packet,a,b)
if __name__=="__main__":unittest.main()
