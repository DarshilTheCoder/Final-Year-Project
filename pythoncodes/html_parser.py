"""This is the main html_parser file which basically parse the players html pages which we get using player_scrapper.py and stored it into data dictionary. It have different functions like parse_table is the main function which takes out all the data row by row and cell by cell and store it into season_dict. There are other small small functions like bio_values, format_debut_last etc, whose description I have attached just above the function. Here, I took help of an AI especially in writing the regex part because the data was in string and getting difficult to extract.
Here, I am storing the extracted data with name ipl_players_data.csv, I parse each team folder one by one and each time I delete the previous ipl_players_data.csv file, such that I am sure that newly generated file of that team which I parsed just now. Then I manually put it into the processed_data folder with team name like CSK_players_data.csv, etc."""

import os,pandas as pd
from bs4 import BeautifulSoup
import json,re
import shutil, os


#parse_table is the function which is used to parse the table of Batting & Fielding and Bowling statistics of each player. 
def parse_table(table):
    #headers list comprehension will help to define the header of the tables
        headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
        # print(headers)  
        season_dict = {}
    #following for loop will help to traverse each row by row and cells help to get the value of each cell
        for row in table.find_all('tr', class_='ds-bg-fill-canvas'):
            cells = row.find_all('td')
            tournament = cells[0].find('span').get_text(strip=True)
            #as I just want the data of IPL and not other leagues, as it is not useful in price prediction of IPL auction.
            if not tournament.startswith('IPL '):
                continue
            year = tournament.replace('IPL ', '')

            #storing each cell value against it's header
            row_dict = {}
            for header, cell in zip(headers, cells):
                span = cell.find('span')
                row_dict[header] = span.get_text(strip=True) if span else cell.get_text(strip=True)
            #now the full result of that perticular year has been store inside season_dict. 
            season_dict[year] = row_dict
        return season_dict


#bio_value function is used to get the each players bio
def bio_value(soup, label):
        p = soup.find('p', string=label)
        value  =  p.find_next_sibling().get_text(" ", strip=True) if p else None
        return value

#format_debut_last fucntion is used to return (debut_str,last_str) for headers like ODI matches and all. It has been written with the help of an AI, especially the regex part as it was getting difficult to extract that particular data. 
def format_debut_last(format_label):
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

#tail_date function is used extract the date from the string. 
def tail_date(match_str):
    if not match_str:
        return None
        # last ' - ' splits ground info from the date portion
        # return match_str.rsplit(' - ', 1)[-2].strip()
    m = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', match_str)
    return m.group(1) if m else match_str


#intl_career function is just to get players' international career data, which is available on players profile
def intl_career(soup):
    node = soup.find(string=re.compile('INTL CAREER'))
    if not node:
        return '-'  #if player don't have international history                                   
    value =  node.replace('INTL CAREER:', '').strip() 
    # print(value) 
    return value


#temporary directory name, where I stored the data while extracting. 
dir_name = 'data'
file = os.listdir(dir_name)
# print(file)

all_records = []
skipped = [] 
for fname in file:
    if not fname.endswith('.html'):
        continue
    try:
        with open(f'{dir_name}/{fname}','r', encoding='utf-8') as f:
            slug = fname.replace('.html', '')        
            player_id = slug.rsplit('-', 1)[1]
            playerid  = player_id
            # print(player_id)            
            html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            
            born = bio_value(soup, 'Born')   
            age  = bio_value(soup, 'Age') 
            player_name = bio_value(soup, 'Full Name')
            role = bio_value(soup,'Playing Role')
            bat_style = bio_value(soup,'Batting Style')
            bowl_style = bio_value(soup,'Bowling Style')
            intl = intl_career(soup)
            # print(role)
            # print(player_name)
            # print(born)
            # print(age)
            #print(intl)
            
            #below loop is used to get the player's nationality, here also AI is used, as the data was inside the json format
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
            t20_section = t20_heading.find_parent('div', class_='ds-w-full') 
            # print(t20_section)
            headers = t20_section.find_all('th', class_='ds-bg-fill-content-alternate')
            # print(headers)
            # tables = t20_section.find_all('table')   # [batting, bowling]
            #created different dictionary to store batting and bowling stats
            batting = bowling = {}
            for tbl in t20_section.find_all('table'):
                headers = [th.get_text(strip=True).lower() for th in tbl.find_all('th')]
                if 'wkts' in headers:          # as it is unique in the bowling table
                    bowling = parse_table(tbl)
                elif 'hs' in headers:          # and it unique in the batting table
                    batting = parse_table(tbl)
            #so record have another two dict with name batting and bowling. 
            record = {'player_id':playerid,'name':player_name,"batting": batting, "bowling": bowling, "birthdate":born,'age':age,'nationality':nationality, 'odi_debut_date':odi_debut_date, 'odi_last_date':odi_last_date,'t20i_debut_date':t20i_debut_date,'t20i_last_date':t20i_last_date,'player_role':role,'batting_style':bat_style,'bowling_style':bowl_style, 'international_career':intl}
            all_records.append(record)
            # print(record)
            # print(len(tables))
            # print(f'BATTING TABLE = {tables[0]}')
            # print(f'BOWLING TABLE = {tables[1]}')
    except Exception as e:
        #as there are some players who got skipped while parsing, that due to utf encoding error, which I then solved using or by writing another code with name skipped_players.py
        skipped.append({'file':fname,'error':str(e)})
        #shutil is module which is used to make the copy of the data
        shutil.copy(f'{dir_name}/{fname}', f'skipped_data/{fname}')
        # print(f'SKIPPED {fname}')

# print(all_records[0])
# print(len(file))
# print(f"Parsed {len(all_records)} players")

def rows_from_records(records):
    rows = []
    for record in all_records:
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
    # print(df.shape)
    if skipped:
        pd.DataFrame(skipped).to_csv('skipped_players.csv', index=False)
        # print(f"{len(skipped)} players skipped — see skipped_players.csv")
    
