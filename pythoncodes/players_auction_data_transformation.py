"""This file is used to add some more features to the final_4_with_status_auction_with_prior_stats.csv file and then store it into final_4_modelling_ready_dataset.csv file which is ready for modelling"""


import pandas as pd
import datetime as dt


INPUT_DIR = r'D:\DataEngineering\Final Year Project\processed_data\final_4_with_status_auction_with_prior_stats.csv'
OUTPUT_DIR = r'D:\DataEngineering\Final Year Project\processed_data\final_4_modelling_ready_dataset.csv'
YEAR_RANGE = [2008,2011,2014,2018,2022,2025]

def is_mega_auction(data):
    data['is_mega_auction'] = None
    data['is_mega_auction'] = data['year'].isin(YEAR_RANGE)
    return data

def changing_team_name(data):
    proper_team_name = {'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
                        'Delhi Daredevils':'Delhi Capitals',
                        'Kings XI Punjab':'Punjab Kings',
                        'Pune Warriors':'Pune Warriors India',
                        'Kochi':'Kochi Tuskers Kerala'}
    data['team'] = data['team'].replace(proper_team_name)
    return data

def is_capped(data):
    data['int_value'] = data['international_career'].str.extract(r'(\d{4})').astype('Int64')
    data['is_capped'] = data['int_value'].notna() & (data['int_value'] <= data['year'])
    return data

def age_during_auction(data):
    birth = pd.to_datetime(data["birthdate"], errors="coerce")
    data["age_during_auction"] = data["year"] - birth.dt.year
    return data

def getting_overseasvalue_from_nationality(data):
    ov  = data['overseas'].map({1.0: True, 0.0: False, True: True, False: False}).astype('boolean')
    nat = data['nationality'].ne('India').where(data['nationality'].notna()).astype('boolean')
    data['overseas2'] = ov.fillna(nat)   
    return data


def changing_label_of_auction_result(data):
    blank = data['auction_result'].isna()
    status_lc = data['status'].astype(str).str.strip().str.lower()
    data.loc[blank & (status_lc == 'rtm'),        'auction_result'] = 'sold'         
    data.loc[blank & (status_lc == 'retained'),   'auction_result'] = 'retained'     
    data.loc[blank & (data['transferred'] == 1),  'auction_result'] = 'transferred'  
    return data

data = pd.read_csv(INPUT_DIR)
data = is_mega_auction(data)
data = is_capped(data)
data = age_during_auction(data)
data = getting_overseasvalue_from_nationality(data)
data = changing_label_of_auction_result(data)
data = changing_team_name(data)
print(data.columns)
data.to_csv(OUTPUT_DIR,index=False)
print(data.head())

