
"""This is the main html_parser file which basically parse the players html pages 
which we get using player_scrapper.py and stored it into data dictionary. 
"""

import os
import re
import json
import pandas as pd
from bs4 import BeautifulSoup

RAW_DIR = r"D:\DataEngineering\Final Year Project\raw_data"                       
OUT_DIR = r"D:\DataEngineering\Final Year Project\processed_data\players_data"    

TEAMS = {
    "CSK_Data": "CSK",   "DC_Data": "DC",     "Deccan_Data": "deccan",
    "GL_Data": "GL",     "GT_Data": "GT",     "KKR_Data": "KKR",
    "Kochi_Data": "Kochi", "LSG_Data": "LSG", "MI_Data": "MI",
    "PBKS_Data": "PBKS", "PWI_Data": "PWI",   "RCB_Data": "RCB",
    "RPS_Data": "RPS",   "RR_Data": "RR",     "SRH_Data": "SRH",
}



def parse_table(table):

    headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
    
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


def get_nationality(soup):
    nationality = None
    for tag in soup.find_all('script', type='application/ld+json'):
        data = json.loads(tag.string)
        nodes = data.get('@graph', [data])
        for n in nodes:
            if n.get('@type') == 'Person' and n.get('nationality'):
                nationality = n['nationality'].get('name')
    return nationality


def format_debut_last(soup, format_label):
    """(debut, last) text for a heading like 'ODI Matches'. soup is passed in
    now (no hidden global), so it works from inside parse_one_player()."""
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
        # return match_str.rsplit(' - ', 1)[-2].strip()
    m = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', match_str)
    return m.group(1) if m else match_str



def intl_career(soup):
    node = soup.find(string=re.compile('INTL CAREER'))
    if not node:
        return '-'                                 
    value =  node.replace('INTL CAREER:', '').strip() 

    return value



def parse_one_player(path):
    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    slug = os.path.basename(path).replace('.html', '')
    playerid = slug.rsplit('-', 1)[1]                 

    odi_debut, odi_last = format_debut_last(soup, 'ODI Matches')
    t20i_debut, t20i_last = format_debut_last(soup, 'T20I Matches')

    t20_heading = soup.find(lambda tag: tag.name == 'h2' and 'T20 Stats' in tag.get_text())
    t20_section = t20_heading.find_parent('div', class_='ds-w-full')

    batting = bowling = {}
    for tbl in t20_section.find_all('table'):
        headers = [th.get_text(strip=True).lower() for th in tbl.find_all('th')]
        if 'wkts' in headers:
            bowling = parse_table(tbl)
        elif 'hs' in headers:
            batting = parse_table(tbl)

    record = {
        'player_id': playerid,
        'name': bio_value(soup, 'Full Name'),
        'batting': batting, 
        'bowling': bowling,
        'birthdate': bio_value(soup, 'Born'),
        'age': bio_value(soup, 'Age'),
        'nationality': get_nationality(soup),
        'player_role': bio_value(soup, 'Playing Role'),
        'batting_style': bio_value(soup, 'Batting Style'),
        'bowling_style': bio_value(soup, 'Bowling Style'),
        'international_career': intl_career(soup),
        'odi_debut_date': tail_date(odi_debut), 
        'odi_last_date': tail_date(odi_last),
        't20i_debut_date': tail_date(t20i_debut), 
        't20i_last_date': tail_date(t20i_last)
    }
    return record



def rows_from_records(records):
    rows = []
    for record in records:
        for year, bat in record['batting'].items():
            bowl = record['bowling'].get(year, {})
            rows.append({
                'player_id': record['player_id'], 
                'player_name': record['name'],
                'birthdate': record['birthdate'], 
                'age': record['age'],
                'nationality': record['nationality'], 
                'player_role': record['player_role'],
                'batting_style': record['batting_style'], 
                'bowling_style': record['bowling_style'],
                'international_career': record['international_career'],
                'year': year, 
                'tournament': bat.get('tournament'), 
                'team': bat.get('teams'),
                'matches': bat.get('mat'), 
                'innings': bat.get('inns'), 
                'no': bat.get('no'),
                'runs': bat.get('runs'), 
                'highestscore': bat.get('hs'),
                'batting_average': bat.get('ave'), 
                'bf': bat.get('bf'), 
                'strikerate': bat.get('sr'),
                '100s': bat.get('100s'), 
                '50s': bat.get('50s'), 
                '4s': bat.get('4s'), 
                '6s': bat.get('6s'),
                'Ct': bat.get('ct'), 
                'St': bat.get('st'),
                'wickets': bowl.get('wkts'), 
                'economy': bowl.get('econ'), 
                'balls': bowl.get('balls'),
                'bbi': bowl.get('bbi'), 
                'bbm': bowl.get('bbm'), 
                'bowl_ave': bowl.get('ave'),
                'sr': bowl.get('sr'), 
                '4w': bowl.get('4w'), 
                '5w': bowl.get('5w'), 
                '10w': bowl.get('10w'),
                't20_start': record.get('t20i_debut_date'), 
                't20_end': record.get('t20i_last_date'),
                'odi_start': record.get('odi_debut_date'), 
                'odi_end': record.get('odi_last_date'),
            })
    return rows


os.makedirs(OUT_DIR, exist_ok=True)
all_skipped = []
for team_folder, short_name in TEAMS.items():
    folder = os.path.join(RAW_DIR, team_folder)
    print(folder)
    if not os.path.isdir(folder):
        print(f"[skip] folder not found: {team_folder}")
        continue
    all_records, skipped = [], []
    for fname in os.listdir(folder):
        if not fname.endswith('.html'):
            continue
        try:
            all_records.append(parse_one_player(os.path.join(folder, fname)))
        except Exception as e:
            skipped.append({'team': short_name, 'file': fname, 'error': str(e)})
    rows = rows_from_records(all_records)
    out_path = os.path.join(OUT_DIR, f"{short_name}_players_data.csv")
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"{short_name:8} {len(all_records):3d} players -> {len(rows):4d} rows | skipped {len(skipped)}  ->  {short_name}_players_data.csv")
    all_skipped.extend(skipped)


if all_skipped:
    pd.DataFrame(all_skipped).to_csv(os.path.join(OUT_DIR, 'skipped_players.csv'), index=False)
    print(f"\n{len(all_skipped)} players skipped across all teams -> skipped_players.csv")
else:
    print("\nNo players skipped.")