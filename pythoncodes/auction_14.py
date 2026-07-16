import re, pandas as pd
from bs4 import BeautifulSoup

def parse_auction_2014_format(html_path, year=None):
    soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
    at = soup.select_one('#auction_table')
    year = (at.get('data-year') if at and at.get('data-year') else year)

    rows = []
    for team in soup.select("div[id^='team_']"):
        h3 = team.find('h3')
        team_name = h3.get_text(strip=True) if h3 else None

        # purse from plain <h4> "Total spent: N" / "Total available: N"  (raw rupees)
        purse_spent = purse_left = None
        for h4 in team.find_all('h4'):
            txt = h4.get_text(" ", strip=True)
            if txt.lower().startswith('total spent'):
                purse_spent = txt.split(':', 1)[1].strip()
            elif txt.lower().startswith('total available'):
                purse_left = txt.split(':', 1)[1].strip()

        for li in team.select('ul.table > li'):
            a = li.select_one('a[href*="player"]')          # link WRAPS span.name here
            if not a:
                continue
            m = re.search(r'/player/(\d+)', a['href'])
            player_id   = m.group(1) if m else None
            name_span   = li.select_one('span.name')
            player_name = name_span.get_text(strip=True) if name_span else a.get_text(strip=True)

            mids    = [mm.get_text(strip=True) for mm in li.select('span.mid')]
            country = mids[0] if len(mids) >= 1 else None     # CTRY column (2014-only)
            ptype   = mids[1] if len(mids) >= 2 else None     # TYPE column
            dolr = li.select_one('span.dolr')
            last = li.select_one('span.last')

            rtm = bool(li.select_one('span[style*="cc0000" i]'))   # RTM = red inline span

            rows.append({
                'year':           year,
                'team':           team_name,
                'purse_spent':    purse_spent,                 # raw rupees (as-is)
                'purse_left':     purse_left,
                'player_id':      player_id,
                'player_name':    player_name,
                'player_fullname':player_name,
                'birthdate':      None,
                'country':        country,                     # extra column this format gives you
                'type':           ptype,
                'cost_inr_lakh':  dolr.get_text(strip=True) if dolr else None,
                'cost_usd_000':   last.get_text(strip=True) if last else None,
                'status':         'RTM' if rtm else 'New',     # no retained marker in 2014
                'transferred':    False,                       # concept not present
                'overseas':       (country or '').upper() not in ('IND', 'INDIA'),  # derived from country
            })
    return pd.DataFrame(rows)

df = parse_auction_2014_format('auction_data/ipl-2014-auction.html', year='2014')
df.to_csv('ipl_2014_auction.csv', index=False)
print(df.shape)