"""Generated answer-layer FAQs must exactly match the visible reviewed answers."""
import json
from pathlib import Path
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from apply_seo_tags import faq_pairs
class AnswerFAQParity(unittest.TestCase):
    def test_answers_match_visible_copy(self):
        for name in ('saint-charbel-feast-day','saint-charbel-novena'):
            html=(ROOT/(name+'.html')).read_text()
            blocks=[json.loads(t) for t in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)]
            faqs=[b for b in blocks if b.get('@type')=='FAQPage']
            self.assertEqual(len(faqs),1,name)
            actual=[(q['name'],q['acceptedAnswer']['text']) for q in faqs[0]['mainEntity']]
            self.assertEqual(actual,faq_pairs(html),name)
            self.assertEqual(len(actual),5,name)
