"""This auction python file is used to scrap the 2011 and 2013 auction html file"""

import re
import pandas as pd
from bs4 import BeautifulSoup

def parse_auction_flat_table(html_path):
    file = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(file, 'html.parser')

    cap = soup.select_one('aside.inline-table h2.table-caption') or soup.find('h2', class_='table-caption')
    if cap and not year:
        m = re.search(r'(20\d{2})', cap.get_text())
        year = m.group(1) if m else None

    table = soup.select_one('aside.inline-table table')
    rows = []
    for tr in table.select('tbody tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if len(cells) < 4:
            continue #just to make sure that each row have all 
        raw_name, country, team, cost = cells[0], cells[1], cells[2], cells[3]

        is_ret = '(retained)' in raw_name.lower()

        player_name = re.sub(r'\s*\(retained\)\s*', '', raw_name, flags=re.I).strip()

        rows.append({
            'year':           year,
            'team':           team,
            'purse_spent':    None,            
            'purse_left':     None,
            'player_id':      None,           
            'player_name':    player_name,
            'player_fullname':player_name,
            'birthdate':      None,
            'country':        country,
            'type':           None,            
            'cost_usd':       cost,            
            'status':         'Retained' if is_ret else 'New',
            'transferred':    False,
            'overseas':       country.strip().lower() not in ('india',)
        })
    return pd.DataFrame(rows)

df = parse_auction_flat_table('auction_data/ipl-2013-auction.html')
df.to_csv('ipl_2013_auction.csv', index=False)
print(df.shape)