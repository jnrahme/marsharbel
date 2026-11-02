"""Exact source/copy/metadata attribution contract, including hostile drift checks."""
import json
from pathlib import Path
import re
import subprocess
import unittest
from collections import Counter
from bs4 import BeautifulSoup
from check_i18n_policy import extract_html
ROOT=Path(__file__).resolve().parents[2]
APPROVED="These messages are attributed to Saint Charbel in Raymond Nader’s reported spiritual experiences, as published by the Family of Saint Sharbel,"

class QuotesAttribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'saint-charbel-quotes.html').read_text()
        cls.source=(ROOT/'src/pages/saint-charbel-quotes.html').read_text()
        cls.catalog=json.loads((ROOT/'locales/en/quotes-attribution-copy.json').read_text())
        cls.page=BeautifulSoup(cls.html,'html.parser')

    def test_approved_wording_and_source(self):
        self.assertIn(APPROVED,self.page.get_text())
        self.assertTrue(self.page.select('a[href="https://www.familyofsaintsharbel.org/experiences.html"]'))
        self.assertIn('not as independently established supernatural events or Church-recognized miracles',self.page.get_text())

    def test_no_historical_authorship_claim(self):
        for claim in ('from his pen -','small body of homilies and sayings preserved by his monastic family','Among the verified sayings','messages of his words, including'):
            self.assertNotIn(claim,self.html)

    def test_metadata_and_schema_match(self):
        description=self.catalog['copy']['description']
        for attrs in ({'name':'description'},{'property':'og:description'},{'name':'twitter:description'}):
            self.assertEqual(self.page.find('meta',attrs)['content'],description)
        schemas=[json.loads(n.string) for n in self.page.select('script[type="application/ld+json"]')]
        faq=next(x for x in schemas if x.get('@type')=='FAQPage')
        answers={x['acceptedAnswer']['text'] for x in faq['mainEntity']}
        for key in ('faqSelection','faqBooks','faqVerification'):
            self.assertIn(self.catalog['copy'][key],answers)
            self.assertIn(self.catalog['copy'][key],self.page.get_text())

    def test_no_renumbering(self):
        for key,number in [('bookletOrigin','1'),('bookletHoliness','12'),('bookletFamily','16'),('bookletLove','1')]:
            self.assertIn('message '+number,self.catalog['copy'][key])
            self.assertIn('booklet numbering',self.catalog['copy'][key])

    def test_catalog_scope_and_exact_counts(self):
        self.assertEqual(set(self.catalog['values']),{'saint-charbel-quotes.html'})
        actual=extract_html(self.html)
        for text,count in self.catalog['values']['saint-charbel-quotes.html'].items():
            self.assertEqual(actual[text],count)
        for key in self.catalog['copy']:
            self.assertIn('{{copy quotes-attribution '+key+'}}',self.source)

    def test_negative_controls_reject_bad_schema_or_missing_approval(self):
        mutated=self.html.replace('reported spiritual experiences','historical manuscript')
        self.assertNotIn(APPROVED,BeautifulSoup(mutated,'html.parser').get_text())
        description=self.catalog['copy']['description']
        wrong=self.html.replace(description,'Words written by Saint Charbel')
        self.assertNotEqual(BeautifulSoup(wrong,'html.parser').find('meta',{'name':'description'})['content'],description)

if __name__=='__main__':unittest.main()
