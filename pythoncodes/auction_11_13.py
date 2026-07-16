import re, pandas as pd
from bs4 import BeautifulSoup

def parse_auction_flat_table(html_path):
    soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

    # year from caption e.g. "IPL 4 - Player Auction 2011"
    cap = soup.select_one('aside.inline-table h2.table-caption') or soup.find('h2', class_='table-caption')
    if cap and not year:
        m = re.search(r'(20\d{2})', cap.get_text())
        year = m.group(1) if m else None

    table = soup.select_one('aside.inline-table table')
    rows = []
    for tr in table.select('tbody tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if len(cells) < 4:
            continue
        raw_name, country, team, cost = cells[0], cells[1], cells[2], cells[3]

        is_ret = '(retained)' in raw_name.lower()
        player_name = re.sub(r'\s*\(retained\)\s*', '', raw_name, flags=re.I).strip()

        rows.append({
            'year':           year,
            'team':           team,
            'purse_spent':    None,            # not in this format
            'purse_left':     None,
            'player_id':      None,            # NOT AVAILABLE — see note
            'player_name':    player_name,
            'player_fullname':player_name,
            'birthdate':      None,
            'country':        country,
            'type':           None,            # no role column this year
            'cost_usd':       cost,            # full USD dollars (as-is)
            'status':         'Retained' if is_ret else 'New',
            'transferred':    False,
            'overseas':       country.strip().lower() not in ('india',)
        })
    return pd.DataFrame(rows)

df = parse_auction_flat_table('auction_data/ipl-2013-auction.html')
df.to_csv('ipl_2013_auction.csv', index=False)
print(df.shape)