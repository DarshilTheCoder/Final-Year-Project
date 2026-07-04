import os,pandas as pd
from bs4 import BeautifulSoup
import json,re
import shutil, os


def parse_table(table):
    #   headers: gives the table header
        headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
        # print(headers)  
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

def intl_career(soup):
    node = soup.find(string=re.compile('INTL CAREER'))
    if not node:
        return '-'                                    # never played international
    return node.replace('INTL CAREER:', '').strip()   # "2009 - 2026"

dir_name = 'data'
file = os.listdir(dir_name)
print(file)

all_records = []
skipped = [] 
for fname in file:
    if not fname.endswith('.html'):
        continue
    try:
        with open(f'{dir_name}/{fname}','r') as f:
            slug = fname.replace('.html', '')        
            player_id = slug.rsplit('-', 1)[1]
            playerid  = player_id
            print(player_id)            
            html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            
            born = bio_value(soup, 'Born')   # "July 07, 1981, Ranchi, Bihar (now Jharkhand)"
            age  = bio_value(soup, 'Age')    # "44y 357d"
            player_name = bio_value(soup, 'Full Name')
            role = bio_value(soup,'Playing Role')
            intl = intl_career(soup)
            # print(role)
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
            # tables = t20_section.find_all('table')   # [batting, bowling]
            batting = bowling = {}
            for tbl in t20_section.find_all('table'):
                headers = [th.get_text(strip=True).lower() for th in tbl.find_all('th')]
                if 'wkts' in headers:          # unique to the bowling table
                    bowling = parse_table(tbl)
                elif 'hs' in headers:          # unique to the batting table
                    batting = parse_table(tbl)
            record = {'player_id':playerid,'name':player_name,"batting": batting, "bowling": bowling, "birthdate":born,'age':age,'nationality':nationality, 'odi_debut_date':odi_debut_date, 'odi_last_date':odi_last_date,'t20i_debut_date':t20i_debut_date,'t20i_last_date':t20i_last_date,'player_role':role, 'international_career':intl}
            all_records.append(record)
            # print(record)
            # print(len(tables))
            # print(f'BATTING TABLE = {tables[0]}')
            # print(f'BOWLING TABLE = {tables[1]}')
    except Exception as e:
        skipped.append({'file':fname,'error':str(e)})
        shutil.copy(f'{dir_name}/{fname}', f'skipped_data/{fname}')
        print(f'SKIPPED {fname}')

# print(all_records[0])
print(len(file))
print(f"Parsed {len(all_records)} players")
rows = []
for record in all_records:
    for year, bat in record['batting'].items():
        bowl = record['bowling'].get(year, {})          # matching bowling for that year
        rows.append({
            'player_id':   record['player_id'],
            'player_name': record['name'],
            'birthdate':   record['birthdate'],
            'age':         record['age'],
            'nationality': record['nationality'],
            'player_role': record['player_role'],
            'international_career':record['international_career'],
            'year':        year,
            'tournament':  bat.get('tournament'),
            'team':        bat.get('teams'),
            'matches':     bat.get('mat'),
            'innings':     bat.get('inns'),
            'no':          bat.get('no'),
            'runs':        bat.get('runs'),
            'highestscore':bat.get('hs'),
            'batting_average':     bat.get('ave'),
            'bf':          bat.get('bf'),
            'strikerate':  bat.get('sr'),
            '100s':        bat.get('100s'),
            '50s':         bat.get('50s'),
            '4s':          bat.get('4s'),
            '6s':          bat.get('6s'),
            'Ct':          bat.get('ct'),
            'St':          bat.get('st'),
            'wickets':     bowl.get('wkts'),
            'economy':     bowl.get('econ'),
            'balls':       bowl.get('balls'),
            'bbi':         bowl.get('bbi'),
            'bbm':         bowl.get('bbm'),
            'bowl_ave':         bowl.get('ave'),
            'sr':          bowl.get('sr'),
            '4w':          bowl.get('4w'),
            '5w':          bowl.get('5w'),
            '10w':         bowl.get('10w'),
            't20_start':      record.get('t20i_debut_date'),
            't20_end':        record.get('t20i_last_date'),
            'odi_start':      record.get('odi_debut_date'),
            'odi_end':        record.get('odi_last_date'),
        })

df = pd.DataFrame(rows)
df.to_csv('ipl_players_data.csv', index=False)
print(df.shape)
if skipped:
    pd.DataFrame(skipped).to_csv('skipped_players.csv', index=False)
    print(f"{len(skipped)} players skipped — see skipped_players.csv")
    
