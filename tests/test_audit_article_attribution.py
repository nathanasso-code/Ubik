import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("audit", Path(__file__).resolve().parents[1] / "scripts/audit_article_attribution.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class AuditTests(unittest.TestCase):
    def test_jsonld_split_into_chunks(self):
        p = audit.Metadata()
        p.feed('<script type="application/ld+json">{"@type":"Article","author":')
        p.feed('{"@type":"Organization","name":"Editorial Team"}}</script>')
        findings = audit.extract('<script type="application/ld+json">{"@type":"Article","author":{"@type":"Organization","name":"Editorial Team"}}</script>')
        self.assertEqual(findings[0]["kind"], "Organization")
        self.assertEqual(len(p.scripts), 1)
        self.assertEqual(len(audit.extract('<script type="application/ld+json">' + p.scripts[0] + '</script>')), 1)

    def test_meta_author_without_inference(self):
        result = audit.extract('<meta name="author" content="Research Desk">')
        self.assertEqual(result[0]["kind"], "unverified")

    def test_balanced_sampling(self):
        items = [{"source_id": s, "url": "https://example.org/"+s+str(i), "title":"T", "authors":[]} for s in ("a","b") for i in range(3)]
        chosen = audit.sample(items, 4)
        self.assertEqual([x["source_id"] for x in chosen], ["a","b","a","b"])

    def test_page_without_author_not_mislabeled(self):
        discovery = {"items":[{"source_id":"a","url":"https://example.org/article","title":"A","authors":[]}]}
        result = audit.audit(discovery, fetcher=lambda _: "<html><title>A</title></html>")
        self.assertEqual(result["results"][0]["status"], "not_found_in_page_metadata")

if __name__ == "__main__":
    unittest.main()
