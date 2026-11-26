import unittest
from src.pro import parse_job, public_url, pdf_bytes, draft_resume, suggestions
from src.engine import analyze,extract_pdf
class ProTests(unittest.TestCase):
 def test_json(self):
  self.assertIn('Python',parse_job('<script type="application/ld+json">{"@type":"JobPosting","description":"'+('Python developer SQL requirements. '*5)+'"}</script>'))
 def test_fallback(self):
  with self.assertRaises(ValueError):parse_job('<html>Access denied</html>')
 def test_private(self):
  with self.assertRaises(ValueError):public_url('http://127.0.0.1')
 def test_pdf(self):self.assertIn('Python',extract_pdf(pdf_bytes('Report','Python & SQL')))
 def test_draft(self):
  r=analyze('Python SQL','Python');self.assertEqual(draft_resume('Skills\n- SQL\n- Python',r),'Skills\n- Python\n- SQL')
 def test_tips(self):self.assertIn('Docker',' '.join(suggestions(analyze('Python','Python Docker'),'Python')))
