import re, pandas as pd
from bs4 import BeautifulSoup

def parse_auction_prose_2015(html_path, year=None):
    soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
    article = soup.select_one('article.ci-story') or soup.find('article')

    link_ids = {}
    for a in article.select('a[href*="/player/"]'):
        m = re.search(r'/player/(\d+)', a['href'])
        if m: link_ids[a.get_text(strip=True)] = m.group(1)

    parts = re.split(r'\n(Players sold|Players unsold)\n', article.get_text('\n', strip=True))

    def to_crore(num, unit):
        return float(num) if 'crore' in unit.lower() else float(num) / 100   # lakh -> crore

    rows = []
    for i in range(1, len(parts) - 1, 2):
        header, body = parts[i], parts[i + 1]
        status = 'Unsold' if 'unsold' in header.lower() else 'Sold'
        cur, det = None, []

        def flush():
            if cur is None: return
            d = ' '.join(det)
            r = {'year': year, 'status': status, 'player_name': cur,
                 'player_id': link_ids.get(cur), 'team': None, 'amount_raw': None,
                 'amount_crore': None, 'detail_raw': d, 'needs_review': False}
            m = re.search(r'-\s*(.+?)\s*-\s*Rs\s*([\d.]+)\s*(crores?|lakh)', d, re.I)
            if m:
                r['team'] = m.group(1).strip()
                r['amount_raw'] = f"Rs {m.group(2)} {m.group(3)}"
                r['amount_crore'] = to_crore(m.group(2), m.group(3))
            elif status == 'Unsold':
                m2 = re.search(r'-\s*(.+)', d)
                if m2: r['team'] = m2.group(1).strip()
            else:
                r['needs_review'] = True
            rows.append(r)

        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('('): continue
            if line[:1].isupper() and not line.startswith(('-', 'Rs')) and len(line) < 40:
                flush(); cur, det = line, []
            else:
                det.append(line)
        flush()
    return pd.DataFrame(rows)

df = parse_auction_prose_2015('auction_data/ipl-2015-auction.html', year='2015')
df.to_csv('ipl_2015_auction.csv', index=False)
print(df.shape, "| needs_review:", df['needs_review'].sum())