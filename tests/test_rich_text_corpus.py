import tempfile,unittest,json
from pathlib import Path
from ingestion.rich_text_corpus import build
class RichTextTests(unittest.TestCase):
 def test_only_substantial_licensed_text(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)
   (p/"PMC1.json").write_text(json.dumps({"url":"https://example.org/a","title":"Study",
     "text":"A"*2500,"license_evidence":["CC BY 4.0"]}))
   (p/"PMC2.json").write_text(json.dumps({"url":"https://example.org/b",
     "text":"Short","license_evidence":["CC BY 4.0"]}))
   out=build(p,max_chars=2000)
   self.assertEqual(out["coverage"]["rich_documents"],1)
   self.assertTrue(out["documents"][0]["text_truncated"])
   self.assertEqual(out["documents"][0]["original_text_chars"],2500)
if __name__=="__main__":unittest.main()
