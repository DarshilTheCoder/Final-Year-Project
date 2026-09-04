"""This file is used to parse the skipped players' data from the html files and store it into a csv file called skipped_players.csv"""


import os
import pandas as pd
from bs4 import BeautifulSoup
import json,re


def parse_table(table):

        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        print(headers)
        season_dict = {}

        for row in table.find_all('tr', class_='ds-bg-fill-canvas'):
            cells = row.find_all('td')
            tournament = cells[0].find('span').get_text(strip=True)
            if not tournament.startswith('IPL '):
                continue
            year = tournament.replace('IPL ', '')


            row_dict = {}
            for header, cell in zip(headers, cells):
                span = cell.find('span')
                row_dict[header] = span.get_text(strip=True) if span else cell.get_text(strip=True)

            season_dict[year] = row_dict
        return season_dict
    
def bio_value(soup, label):
        p = soup.find('p', string=label)      
        return p.find_next_sibling().get_text(" ", strip=True) if p else None
    

def intl_career(soup):
        node = soup.find(string=re.compile('INTL CAREER'))
        if not node:
            return '-'                                 
        value =  node.replace('INTL CAREER:', '').strip() 
        return value

def format_debut_last(format_label):

        heading = soup.find(string=re.compile(r'^\s*' + re.escape(format_label) + r'\s*$'))
        if not heading:
            return None, None
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
        m = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', match_str)
        return m.group(1) if m else match_str

dir_name = 'skipped_data'
file = os.listdir(dir_name)
print(file)

with open(f'{dir_name}/{file[0]}','r') as f:
    slug = file[0].replace('.html', '')        
    player_id = slug.rsplit('-', 1)[1]
    print(player_id)
    print(slug)
    playerid  = player_id            
    html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    born = bio_value(soup, 'Born')   
    age  = bio_value(soup, 'Age')    
    player_name = bio_value(soup, 'Full Name')
    role = bio_value(soup,'Playing Role')
    bat_style = bio_value(soup,'Batting Style')
    bowl_style = bio_value(soup,'Bowling Style')
    intl = intl_career(soup)


    for tag in soup.find_all('script', type='application/ld+json'):
        data = json.loads(tag.string)
        nodes = data.get('@graph', [data])          # sometimes a list, sometimes one object
        for n in nodes:
            if n.get('@type') == 'Person':
                nationality = n['nationality']['name']

    

    odi_debut, odi_last = format_debut_last('ODI Matches')
    odi_debut_date = tail_date(odi_debut)
    odi_last_date  = tail_date(odi_last)

    t20i_debut, t20i_last = format_debut_last('T20I Matches')
    t20i_debut_date = tail_date(t20i_debut)
    t20i_last_date  = tail_date(t20i_last)

    t20_heading = soup.find(lambda tag: tag.name == 'h2' and 'T20 Stats' in tag.get_text())
    t20_section = t20_heading.find_parent('div', class_='ds-w-full')   
    headers = t20_section.find_all('th', class_='ds-bg-fill-content-alternate')
    tables = t20_section.find_all('table')  
    batting = parse_table(tables[0])
    bowling = parse_table(tables[1])
    record = {'player_id':playerid,'name':player_name,"batting": batting, "bowling": bowling, "birthdate":born,'age':age,'nationality':nationality, 'odi_debut_date':odi_debut_date, 'odi_last_date':odi_last_date,'t20i_debut_date':t20i_debut_date,'t20i_last_date':t20i_last_date,'player_role':role, 'batting_style':bat_style,'bowling_style':bowl_style,'international_career':intl}


rows = []
for year, bat in record['batting'].items():
    bowl = record['bowling'].get(year, {})         
    rows.append({
        'player_id':   record['player_id'],
        'player_name': record['name'],
        'birthdate':   record['birthdate'],
        'age':         record['age'],
        'nationality': record['nationality'],
        'player_role': record['player_role'],
        'batting_style':record['batting_style'],
        'bowling_style':record['bowling_style'],
        'international_career':record['international_career'],
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
df.to_csv('skipped_players.csv', index=False)
print(df.shape)