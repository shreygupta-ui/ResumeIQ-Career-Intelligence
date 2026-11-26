import unittest
from pathlib import Path
from src.engine import analyze,extract_pdf,skills,report
class EngineTests(unittest.TestCase):
    def test_identical(self): self.assertEqual(analyze('Python SQL','Python SQL')['similarity'],100)
    def test_unrelated(self): self.assertEqual(analyze('banana','Docker')['similarity'],0)
    def test_sample(self):
        root=Path(__file__).resolve().parents[1]/'samples'
        r=analyze(extract_pdf((root/'resume.pdf').read_bytes()),(root/'job.txt').read_text())
        self.assertEqual(r['coverage'],75); self.assertEqual(r['missing'],['Docker']); self.assertIn('Docker',report(r))
    def test_boundaries(self): self.assertEqual(skills('JavaScript C++ C#'),{'JavaScript','C++','C#'})
    def test_empty(self):
        for a,b in [('', 'Python'),('the','Python'),('the','and')]:
            with self.assertRaises(ValueError): analyze(a,b)
    def test_no_skills(self): self.assertIsNone(analyze('banana','apple')['coverage'])
    def test_invalid_pdf(self):
        with self.assertRaises(ValueError): extract_pdf(b'bad pdf')
    def test_alias(self): self.assertIn('Machine Learning',skills('ML'))
if __name__=='__main__': unittest.main()
