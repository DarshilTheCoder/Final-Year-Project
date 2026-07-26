"""This python file is used to scrap from 2017 to 2024 auction data, as it was on proper table format, it was bit easy to scrap the data. """

import re
import pandas as pd
from bs4 import BeautifulSoup

def parse_auction_old_format(html_path):
    file = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(file, 'html.parser')

    at = soup.select_one('#auction_table')
    year = at.get('data-year') if at else None      

    rows = []
    for team in soup.select("div[id^='team_']"):
        details = team.select_one('.team-details')
        team_name = details.select_one('h3').get_text(strip=True) if details else None

        # purse spent / available (kept as-is, e.g. "97.15 cr")
        purse_spent = purse_left = None
        for h4 in team.select('.team-details h4.tot-cost'):
            spans = h4.find_all('span')
            if len(spans) >= 2:
                label = spans[0].get_text(strip=True).lower()
                value = spans[1].get_text(strip=True)
                if 'spent' in label:       
                    purse_spent = value
                elif 'available' in label: 
                    purse_left = value

        for li in team.select('ul.table > li'):
            a = li.select_one('span.name a')
            if not a or not a.get('href'):
                continue                              # skip header/empty rows

            # player id from href: /ci/content/player/253802.html
            m = re.search(r'/player/(\d+)', a['href'])
            player_id   = m.group(1) if m else None
            player_name = a.get_text(strip=True)

            # type = first non-empty span.mid
            ptype = None
            for mid in li.select('span.mid'):
                if mid.get_text(strip=True):
                    ptype = mid.get_text(strip=True); break

            # cost as shown: dolr = ₹ lakhs, last = $ (000s)
            dolr = li.select_one('span.dolr')
            last = li.select_one('span.last')

            # status markers are  inside span.name
            # markers = set()
            # name_span = li.select_one('span.name')
            # for tag in name_span.find_all(True):        # every descendant tag, any type
            #     if tag.name != 'a':                     # skip the player link itself
            #         markers.update(tag.get('class', []))
            
            #below one is specifically for 2018 only. 
            markers = set()
            rtm = False
            name_span = li.select_one('span.name')
            for tag in name_span.find_all(True):
                if tag.name == 'a':
                    continue
                markers.update(tag.get('class', []))                 # overseas / retained / transferred
                style = (tag.get('style') or '').lower()
                if 'cc0000' in style:                                # RTM = red inline-styled span
                    rtm = True

            # status now three-way, consistent with the new-format files
            if 'retained' in markers:
                status = 'Retained'
            elif rtm:
                status = 'RTM'
            else:
                status = 'New'

            rows.append({
                'year':           year,
                'team':           team_name,
                'purse_spent':    purse_spent,                        # "97.15 cr" (as-is)
                'purse_left':     purse_left,                          # "2.85 cr"  (as-is)
                'player_id':      player_id,
                'player_name':    player_name,
                'player_fullname':player_name,                        # only one name in this format
                'birthdate':      None,                               # not available here
                'type':           ptype,
                'cost_inr_lakh':  dolr.get_text(strip=True) if dolr else None,  # ₹ lakhs (as-is)
                'cost_usd_000':   last.get_text(strip=True) if last else None,  # $ 000s  (as-is)
                # 'status':         'Retained' if 'retained' in markers else 'New',
                'status':           status,
                'transferred':    'transferred' in markers,
                'overseas':       'overseas' in markers,
            })
    return pd.DataFrame(rows)
year = 2018
df = parse_auction_old_format(f'auction_data/ipl-{year}-auction.html')
df.to_csv(f'ipl_{year}_auction.csv', index=False)
print(df.shape)