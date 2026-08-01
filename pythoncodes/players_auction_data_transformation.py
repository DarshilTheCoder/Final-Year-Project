import pandas as pd
import datetime as dt


INPUT_DIR = r'D:\DataEngineering\Final Year Project\processed_data\final_4_with_status_auction_with_prior_stats.csv'
OUTPUT_DIR = r'D:\DataEngineering\Final Year Project\processed_data\final_4_modelling_ready_dataset.csv'
YEAR_RANGE = [2008,2011,2014,2018,2022,2025]

def is_mega_auction(data):
    # data = pd.read_csv(INPUT_DIR)
    data['is_mega_auction'] = None
    # print(data.columns)
    # print(data.iloc[0])
    data['is_mega_auction'] = data['year'].isin(YEAR_RANGE)
    # print(data.iloc[0])
    return data

def changing_team_name(data):
    # data = pd.read_csv(INPUT_DIR)
    # for team in data['team'].unique():
    #     print(repr(team))
    # print(data['team'].unique())
    proper_team_name = {'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
                        'Delhi Daredevils':'Delhi Capitals',
                        'Kings XI Punjab':'Punjab Kings',
                        'Pune Warriors':'Pune Warriors India',
                        'Kochi':'Kochi Tuskers Kerala'}
    data['team'] = data['team'].replace(proper_team_name)
    # print(data.columns)
    # print(data['full_team_name'].where(data['full_team_name']=='Royal Challengers Bengaluru'))
    # print(data.iloc[68:70])
    return data

def is_capped(data):
    # data = pd.read_csv(INPUT_DIR)
    # print(data.iloc[1])
    # value =  data.iloc[150]['international_career']
    # print(value)
    # print(value.split()[0])
    # print(value.dtype)
    # print(data.iloc[150]['year'])
    data['int_value'] = data['international_career'].str.extract(r'(\d{4})').astype('Int64')
    # capped = has an international debut AND it happened in/by the auction year
    data['is_capped'] = data['int_value'].notna() & (data['int_value'] <= data['year'])
    return data

def age_during_auction(data):
    birth = pd.to_datetime(data["birthdate"], errors="coerce")
    data["age_during_auction"] = data["year"] - birth.dt.year
    return data

def getting_overseasvalue_from_nationality(data):
    # keep the auction 'overseas' exactly as-is (as a nullable boolean), only fill the blanks.
    # True = non-Indian, False = Indian, left blank if nationality is unknown too.
    ov  = data['overseas'].map({1.0: True, 0.0: False, True: True, False: False}).astype('boolean')
    nat = data['nationality'].ne('India').where(data['nationality'].notna()).astype('boolean')
    data['overseas2'] = ov.fillna(nat)   # fillna touches only blanks; auction values win
    return data

data = pd.read_csv(INPUT_DIR)
data = is_mega_auction(data)
data = is_capped(data)
data = age_during_auction(data)
data = getting_overseasvalue_from_nationality(data)
data = changing_team_name(data)
print(data.columns)
data.to_csv(OUTPUT_DIR,index=False)
print(data.head())

