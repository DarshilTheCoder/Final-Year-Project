"""This auction python file is used to scrap the 2012 auction html file"""

from bs4 import BeautifulSoup
import re, pandas as pd

def looks_like_name(s):
    return (s[:1].isupper() and '$' not in s and len(s) < 40
            and not s.startswith(('-', 'to ', 'bid ', 'and ', 'It ', 'Bought ')))

def parse_auction_prose(html_path, year=None):
    soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
    article = soup.select_one('article.ci-story') or soup.find('article')

    link_ids = {}                                  
    for a in article.select('a[href*="/player/"]'):
        m = re.search(r'/player/(\d+)', a['href'])
        if m: link_ids[a.get_text(strip=True)] = m.group(1)

    parts = re.split(r'\n(Bought|Transferred|Retained|Unsold)\n',article.get_text('\n', strip=True))
    rows = []
    for i in range(1, len(parts) - 1, 2):
        section, body = parts[i], parts[i + 1]
        cur, det = None, []

        def flush():
            if cur is None: return
            d = ' '.join(det)
            r = {'year': year, 'section': section, 'player_name': cur,
                 'player_id': link_ids.get(cur), 'team': None, 'sold_usd': None,
                 'base_usd': None, 'detail_raw': d, 'needs_review': False}
            if section == 'Bought':
                m = re.search(r'\$([\d,]+)\s+to\s+([A-Z][A-Za-z ]+?)\s*\(base price \$([\d,]+)\)', d)
                if m: r['sold_usd'], r['team'], r['base_usd'] = m.groups()
                else: r['needs_review'] = True
            elif section == 'Retained':
                m = re.search(r'-\s*([A-Z][A-Za-z ]+?),\s*\$([\d,]+)', d)
                if m: r['team'], r['sold_usd'] = m.group(1).strip(), m.group(2)
                else: r['needs_review'] = True
            elif section == 'Transferred':
                m = re.search(r'-\s*([A-Z][A-Za-z ]+)', d)
                if m: r['team'] = m.group(1).strip()
                else: r['needs_review'] = True
            else:  # Unsold
                m = re.search(r'base price \$([\d,]+)', d)
                if m: r['base_usd'] = m.group(1)
                else: r['needs_review'] = True
            rows.append(r)

        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('('): continue
            if looks_like_name(line): flush(); cur, det = line, []
            else: det.append(line)
        flush()
    return pd.DataFrame(rows)

df = parse_auction_prose('auction_data/ipl-2012-auction.html', year='2012')
df.to_csv('ipl_2012_auction.csv', index=False)
print(df.shape, "| needs_review:", df['needs_review'].sum())