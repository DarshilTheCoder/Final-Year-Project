"""This python file is used to scrap from 2017 to 2024 auction data. """

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
                continue                              

            
            m = re.search(r'/player/(\d+)', a['href'])
            player_id   = m.group(1) if m else None
            player_name = a.get_text(strip=True)

            
            ptype = None
            for mid in li.select('span.mid'):
                if mid.get_text(strip=True):
                    ptype = mid.get_text(strip=True); break

            
            dolr = li.select_one('span.dolr')
            last = li.select_one('span.last')

            
            markers = set()
            rtm = False
            name_span = li.select_one('span.name')
            for tag in name_span.find_all(True):
                if tag.name == 'a':
                    continue
                markers.update(tag.get('class', []))                 
                style = (tag.get('style') or '').lower()
                if 'cc0000' in style:                                
                    rtm = True

            
            if 'retained' in markers:
                status = 'Retained'
            elif rtm:
                status = 'RTM'
            else:
                status = 'New'

            rows.append({
                'year':           year,
                'team':           team_name,
                'purse_spent':    purse_spent,                        
                'purse_left':     purse_left,                          
                'player_id':      player_id,
                'player_name':    player_name,
                'player_fullname':player_name,                        
                'birthdate':      None,                               
                'type':           ptype,
                'cost_inr_lakh':  dolr.get_text(strip=True) if dolr else None,  
                'cost_usd_000':   last.get_text(strip=True) if last else None,  
                'status':           status,
                'transferred':    'transferred' in markers,
                'overseas':       'overseas' in markers,
            })
    return pd.DataFrame(rows)
year = 2018
df = parse_auction_old_format(f'auction_data/ipl-{year}-auction.html')
df.to_csv(f'ipl_{year}_auction.csv', index=False)
print(df.shape)