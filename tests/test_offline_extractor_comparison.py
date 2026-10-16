import unittest
from ingestion.offline_extractor_comparison import metrics,normalized,TextOnly

class OfflineExtractorMetricsTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalized(' a\n  b  '),'a b')
    def test_threshold_requires_words(self):
        self.assertFalse(metrics('a'*900)['substantial_800'])
        self.assertTrue(metrics('word '*220)['substantial_800'])
    def test_script_removed(self):
        parser=TextOnly()
        parser.feed('<p>Keep</p><script>drop</script><p>this</p>')
        self.assertEqual(normalized(' '.join(parser.parts)),'Keep this')

if __name__=='__main__':unittest.main()
