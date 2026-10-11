"""Synthetic head identity and body-byte preservation coverage."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_metadata import compose_travel_clusters
class TravelMetadataOrderTests(unittest.TestCase):
 def test_both_attribute_orders_same_cluster_body_unchanged(self):
  cluster={'/travel':{'en':'/travel','ru':'/ru/travel','x-default':'/travel'}}
  for tag in ['<link rel="canonical" href="https://marsharbel.com/travel"/>','<link href="https://marsharbel.com/travel" rel="canonical"/>']:
   raw='<html><head>'+tag+'<link href="https://marsharbel.com/travel" hreflang="en" rel="alternate"/><link href="https://marsharbel.com/travel" hreflang="x-default" rel="alternate"/></head><body><main>Exact body</main></body></html>';p=ROOT/'travel.html'
   with patch('i18n.travel_metadata.travel_clusters',return_value=cluster):
    out=compose_travel_clusters(ROOT,{'site':'https://marsharbel.com'},{p:raw})[p]
    self.assertIn('hreflang="ru"',out);self.assertEqual(out.split('</head>')[1],raw.split('</head>')[1])
 def test_nontravel_unchanged_and_duplicate_refuses(self):
  p=ROOT/'other.html';raw='<head><link rel="canonical" href="https://marsharbel.com/other"/></head><main>Body</main>'
  with patch('i18n.travel_metadata.travel_clusters',return_value={}):
   self.assertEqual(compose_travel_clusters(ROOT,{'site':'https://marsharbel.com'},{p:raw})[p],raw)
   with self.assertRaises(ValueError):compose_travel_clusters(ROOT,{'site':'https://marsharbel.com'},{p:raw.replace('</head>','<link rel="canonical" href="https://marsharbel.com/other"/></head>')})
if __name__=='__main__':unittest.main()
