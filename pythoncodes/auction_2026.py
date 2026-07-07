import json, pandas as pd
from bs4 import BeautifulSoup

def parse_auction_new_format(html_path):
    soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
    data = json.loads(soup.find('script', id='__NEXT_DATA__').string)
    content = data['props']['appPageProps']['data']['content']

    teams = content['teams']                 # team summary cards
    teams_players = content['teamsPlayers']  # dict keyed by team id (as string)

    rows = []
    for t in teams:
        info = t['team']
        team_id = info['id']

        # team-level summary
        team_name      = info['longName']
        purse_spent    = t['amountSpent']
        purse_left     = t['totalAmount'] - t['amountSpent']
        players_bought = f"{t['slotsBooked']}/{t['totalSlots']}"
        overseas_buys  = f"{t['overseasSlotsBooked']}/{t['totalOverseasSlots']}"

        # players for this team — teamsPlayers keys are STRINGS, team id is int
        for p in teams_players.get(str(team_id), []):
            dob = p['player'].get('dateOfBirth')

            # three-way status: Retained / RTM / New (mutually exclusive)
            if p.get('isRetained'):
                status = 'Retained'
            elif p.get('isMtc'):
                status = 'RTM'
            else:
                status = 'New'

            rows.append({
                'team':           team_name,
                'purse_spent':    purse_spent,
                'purse_left':     purse_left,
                'players_bought': players_bought,
                'overseas_buys':  overseas_buys,
                'player_id':      p['player']['objectId'],
                'player_name':    p['player']['name'],
                'player_fullname':p['player']['longName'],
                'birthdate':      f"{dob['year']:04d}-{dob['month']:02d}-{dob['date']:02d}" if dob else None,
                'type':           p.get('playerRoleType'),
                'base_price':     p.get('basePrice'),      # raw (0 = retained); clean later
                'sold_price':     p.get('soldPrice'),      # raw rupees
                'sold_price_cr':  (p.get('soldPrice') or 0) / 1e7,
                'status':         status,
                'transferred':    p.get('isTransferred', False),
                'overseas':       p.get('isOverseas'),
            })
    return pd.DataFrame(rows)

df = parse_auction_new_format('auction_data/ipl-2026-auction.html')
df.to_csv('ipl_2026_auction.csv', index=False)
print(df.shape)