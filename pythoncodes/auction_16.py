"""This python file is used to parse the 2016 auction html file."""

import re
import pandas as pd
from bs4 import BeautifulSoup

def parse_auction_prose_2016(html_path):
    file = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(file, 'html.parser')
    article = soup.select_one('article.ci-story') or soup.find('article')

    link_ids = {}
    for a in article.select('a[href*="/player/"]'):
        m = re.search(r'/player/(\d+)', a['href'])
        if m: 
            link_ids[a.get_text(strip=True)] = m.group(1)

    parts = re.split(r'\n(Sold players|Unsold players)\n', article.get_text('\n', strip=True))

    def to_crore(num, unit):
        return float(num) if 'crore' in unit.lower() else float(num) / 100

    rows = []
    for i in range(1, len(parts) - 1, 2):
        header, body = parts[i], parts[i + 1]
        status = 'Unsold' if 'unsold' in header.lower() else 'Sold'
        cur, det = None, []

        def flush():
            if cur is None: return
            d = ' '.join(det)
            r = {'year': 2016, 'status': status, 'player_name': cur,
                'player_id': link_ids.get(cur), 'team': None, 'base_crore': None,
                'sold_crore': None, 'detail_raw': d, 'needs_review': False}
            mb = re.search(r'Base price INR\s*([\d.]+)\s*(crores?|lakhs?)', d, re.I)
            if mb: r['base_crore'] = to_crore(mb.group(1), mb.group(2))
            if status == 'Sold':
                ms = re.search(r'sold to\s*(.+?)\s*(?:for\s*)?INR\s*([\d.]+)\s*(crores?|lakhs?)', d, re.I)
                if ms:
                    r['team'], r['sold_crore'] = ms.group(1).strip(), to_crore(ms.group(2), ms.group(3))
                else:
                    r['needs_review'] = True
            rows.append(r)

        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('INR 1') or line.isdigit():
                continue
            if line[:1].isupper() and not line.startswith('(') and len(line) < 40 and 'INR' not in line and 'sold to' not in line:
                flush(); cur, det = line, []
            else:
                det.append(line)
        flush()
    return pd.DataFrame(rows)

df = parse_auction_prose_2016('auction_data/ipl-2016-auction.html')
df.to_csv('ipl_2016_auction.csv', index=False)
print(df.shape, "| needs_review:", df['needs_review'].sum())