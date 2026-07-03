import os
from bs4 import BeautifulSoup
import json,re

file = os.listdir('data')
print(file)

with open(f'data/{file[0]}','r') as f:
    slug = file[0].replace('.html', '')        
    player_id = slug.rsplit('-', 1)[1]
    playerid  = player_id            
    html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    def parse_table(table):
    #   headers: gives the table header
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        print(headers)
        season_dict = {}
        # rows: only this table's season rows
        for row in table.find_all('tr', class_='ds-bg-fill-canvas'):
            cells = row.find_all('td')
            tournament = cells[0].find('span').get_text(strip=True)
            if not tournament.startswith('IPL '):
                continue
            year = tournament.replace('IPL ', '')

            # pairing each header with its cell
            row_dict = {}
            for header, cell in zip(headers, cells):
                span = cell.find('span')
                row_dict[header] = span.get_text(strip=True) if span else cell.get_text(strip=True)

            season_dict[year] = row_dict
        return season_dict
    
    def bio_value(soup, label):
        p = soup.find('p', string=label)      # the label <p>
        return p.find_next_sibling().get_text(" ", strip=True) if p else None

    born = bio_value(soup, 'Born')   # "July 07, 1981, Ranchi, Bihar (now Jharkhand)"
    age  = bio_value(soup, 'Age')    # "44y 357d"
    player_name = bio_value(soup, 'Full Name')
    role = bio_value(soup,'Playing Role')
    print(role)
    # print(full_name)
    # print(born)
    # print(age)

    for tag in soup.find_all('script', type='application/ld+json'):
        data = json.loads(tag.string)
        nodes = data.get('@graph', [data])          # sometimes a list, sometimes one object
        for n in nodes:
            if n.get('@type') == 'Person':
                nationality = n['nationality']['name']
    # print(nationality)
    
    def format_debut_last(format_label):
        """Return (debut_str, last_str) for a format heading like 'ODI Matches'."""
        heading = soup.find(string=re.compile(r'^\s*' + re.escape(format_label) + r'\s*$'))
        if not heading:
            return None, None
        # climb to the block that holds this format's debut/last grid
        block = heading.find_parent('div')
        for _ in range(5):
            if block is None:
                return None, None
            cells = block.find_all('div', class_=lambda c: c and 'ds-col-span-2' in (c if isinstance(c, list) else [c]))
            if len(cells) >= 2:
                return cells[0].get_text(" ", strip=True), cells[1].get_text(" ", strip=True)
            block = block.parent
        return None, None

    def tail_date(match_str):
        if not match_str:
            return None
        # last ' - ' splits ground info from the date portion
        # return match_str.rsplit(' - ', 1)[-2].strip()
        m = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', match_str)
        return m.group(1) if m else match_str

    odi_debut, odi_last = format_debut_last('ODI Matches')
    odi_debut_date = tail_date(odi_debut)
    odi_last_date  = tail_date(odi_last)

    t20i_debut, t20i_last = format_debut_last('T20I Matches')
    t20i_debut_date = tail_date(t20i_debut)
    t20i_last_date  = tail_date(t20i_last)
    # print(odi_debut_date)
    # print(odi_last_date)
    # print(t20i_debut_date)
    # print(t20i_last_date)
    t20_heading = soup.find(lambda tag: tag.name == 'h2' and 'T20 Stats' in tag.get_text())
    # print(t20_heading.get_text())
    t20_section = t20_heading.find_parent('div', class_='ds-w-full')   # the wrapper
    # print(t20_section)
    headers = t20_section.find_all('th', class_='ds-bg-fill-content-alternate')
    # print(headers)
    tables = t20_section.find_all('table')   # [batting, bowling]
    batting = parse_table(tables[0])
    bowling = parse_table(tables[1])
    record = {'player_id':playerid,'name':player_name,"batting": batting, "bowling": bowling, "birthdate":born,'age':age,'nationality':nationality, 'odi_debut_date':odi_debut_date, 'odi_last_date':odi_last_date,'t20i_debut_date':t20i_debut_date,'t20i_last_date':t20i_last_date,'player_role':role}
    # print(record)
    # print(len(tables))
    # print(f'BATTING TABLE = {tables[0]}')
    # print(f'BOWLING TABLE = {tables[1]}')
    import pandas as pd

rows = []
for year, bat in record['batting'].items():
    bowl = record['bowling'].get(year, {})          # matching bowling for that year
    rows.append({
        'player_id':   record['player_id'],
        'player_name': record['name'],
        'birthdate':   record['birthdate'],
        'age':         record['age'],
        'nationality': record['nationality'],
        'player_role': record['player_role'],
        'year':        year,
        'tournament':  bat.get('Tournament'),
        'team':        bat.get('Teams'),
        'matches':     bat.get('Mat'),
        'innings':     bat.get('Inns'),
        'no':          bat.get('NO'),
        'runs':        bat.get('Runs'),
        'highestscore':bat.get('HS'),
        'average':     bat.get('Ave'),
        'bf':          bat.get('BF'),
        'strikerate':  bat.get('SR'),
        '100s':        bat.get('100s'),
        '50s':         bat.get('50s'),
        '4s':          bat.get('4s'),
        '6s':          bat.get('6s'),
        'Ct':          bat.get('Ct'),
        'St':          bat.get('St'),
        'wickets':     bowl.get('Wkts'),
        'economy':     bowl.get('Econ'),
        'balls':       bowl.get('Balls'),
        'bbi':         bowl.get('bbi'),
        'bbm':         bowl.get('bbm'),
        'ave':         bowl.get('Ave'),
        'sr':          bowl.get('SR'),
        '4w':          bowl.get('4W'),
        '5w':          bowl.get('5W'),
        '10w':         bowl.get('10W'),
        't20_start':      record.get('t20i_debut_date'),
        't20_end':        record.get('t20i_last_date'),
        'odi_start':      record.get('odi_debut_date'),
        'odi_end':        record.get('odi_last_date'),
    })

df = pd.DataFrame(rows)
df.to_csv('ipl_players.csv', index=False)
print(df.shape)