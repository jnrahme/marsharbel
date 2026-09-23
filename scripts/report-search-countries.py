#!/usr/bin/env python3
"""Summarize locally exported English-language Search Console Countries CSVs."""
import argparse
import csv
from pathlib import Path

def load(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as source:
        reader=csv.DictReader(source)
        if not {'Country','Clicks','Impressions'}.issubset(reader.fieldnames or []):
            raise ValueError('Expected an English Search Console Countries CSV with Country, Clicks, Impressions columns.')
        rows=[]
        for row in reader:
            # GSC exports whole numbers; reject abbreviated values rather than guessing.
            rows.append({'country':row['Country'],'clicks':int(row['Clicks'].replace(',','')),'impressions':int(row['Impressions'].replace(',',''))})
        return rows

def summary(rows):
    return {'clicks':sum(r['clicks'] for r in rows),'impressions':sum(r['impressions'] for r in rows),'countries with impressions':sum(r['impressions']>0 for r in rows),'countries with clicks':sum(r['clicks']>0 for r in rows)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('current');parser.add_argument('--previous')
    args=parser.parse_args();rows=load(args.current);current=summary(rows)
    previous=summary(load(args.previous)) if args.previous else None
    print('Country export totals (check equal date ranges and filters before comparison):')
    for key,value in current.items():
        delta=f' ({value-previous[key]:+d})' if previous else ''
        print(f'{key}: {value}{delta}')
    print('\nTop countries by clicks, then impressions:')
    for row in sorted(rows,key=lambda r:(r['clicks'],r['impressions']),reverse=True)[:20]:
        ctr=100*row['clicks']/row['impressions'] if row['impressions'] else 0
        print(f"{row['country']}: {row['clicks']} clicks, {row['impressions']} impressions, {ctr:.2f}% CTR")

if __name__=='__main__':main()
