"""This is python file is used to do auction related data transformation. Make sure whenever you run or write any new code for xyz data transformation then please commentout other codes. Also, one thing I maintained that if I am doing any data transformation then it will fall into new_auction_data folder, once you are satisfied with the data then you move it into main folder and replace that file."""


import pandas as pd
from pathlib import Path


#below code is used to do simple conversion of sold prices of file from 2017 to 2024 
# INPUT_DIR  = r"D:\DataEngineering\Final Year Project\processed_data"       
OUTPUT_DIR = r"D:\DataEngineering\Final Year Project\processed_data\new_auction_data"       
# YEARS_RANGE  = range(2017, 2025)      
# SRC_COL    = "cost_inr_lakh"               

# in_dir = Path(INPUT_DIR)
out_dir = Path(OUTPUT_DIR)
out_dir.mkdir(parents=True, exist_ok=True)

# for year in YEARS_RANGE:
#     f = in_dir / f"ipl_{year}_auction.csv"
#     if not f.exists():
#         print(f"[skip] {f.name} not found")
#         continue
#     df = pd.read_csv(f)
#     if SRC_COL not in df.columns:
#         print(f"[warn] {f.name}: no '{SRC_COL}' column -> skipped (check its schema)")
#         continue
#     lakh = pd.to_numeric(df[SRC_COL], errors="coerce") 
#     df["sold_price_in_cr"] = lakh / 100                    
#     df["sold_price"]       = (lakh * 100_000).round().astype("Int64")  


#     print(f"[ok] {year}: {len(df):3d} rows | "
#           f"cr {df['sold_price_in_cr'].min():.2f}-{df['sold_price_in_cr'].max():.2f} | "
#           f"missing price: {int(lakh.isna().sum())}")
#     df.to_csv(out_dir / f"ipl_{year}_auction.csv", index=False)


# print("\nDone. Spot-check one file before trusting the batch.")



#below is used to do auction 2011 2012 (but for 2012 intially required to get overseas column which I get it using last code), and 2013 price conversion

# INPUT_DIR2 = r'D:\DataEngineering\Final Year Project\processed_data\auction_data'
# in_dir2 = Path(INPUT_DIR2)
# YEARS_RANGE2 = [2011,2012,2013]
# SRC_COL2 = 'cost_usd'
# for year in YEARS_RANGE2:
#     f = in_dir2 / f"ipl_{year}_auction.csv"
#     print(f)
#     if not f.exists():
#         print(f"[skip] {f.name} not found")
#         continue
#     data = pd.read_csv(f)
#     # print(data['year'].head())
#     # print(data['overseas'].dtype)
#     if SRC_COL2 not in data.columns:
#         print(f"[warn] {f.name}: no '{SRC_COL2}' column -> skipped (check its schema)")
#         continue
#     if year == 2011:
#         domestic_rate,overseas_rate = 46,45.37
#     elif year == 2013:
#         domestic_rate,overseas_rate = 46,53.3238
#     elif year == 2012:
#         domestic_rate,overseas_rate = 46,48.9640
    
#     rate = data['overseas'].map({False:domestic_rate,True:overseas_rate})
#     # print(rate)
#     data['sold_price'] = (data['cost_usd']*rate).round().astype('Int64')
#     data['sold_price_in_cr'] = data['sold_price']/10000000
    
#     print(f"[ok] {year}: {len(data):3d} rows | domestic x{domestic_rate}, overseas x{overseas_rate} | "
#             f"cr {data['sold_price_in_cr'].min():.2f}-{data['sold_price_in_cr'].max():.2f}")
#     print(data.head())
#     data.to_csv(out_dir / f"ipl_{year}_auction.csv", index=False)
 
# print("\nDone. Spot-check one file before trusting the batch.")



#below code is used to add overseas column in 2012 auction file using new_players_combined csv. 
# AUCTION_DATA = r'D:\DataEngineering\Final Year Project\processed_data\auction_data\ipl_2012_auction.csv'
# STAT_DATA = r'D:\DataEngineering\Final Year Project\processed_data\new_players_combined.csv'

# stat_data = pd.read_csv(STAT_DATA)
# auction_2012_data = pd.read_csv(AUCTION_DATA)
# required_stat_data = stat_data[['player_id','nationality']].dropna().drop_duplicates('player_id')

# auction_2012_data = auction_2012_data.merge(required_stat_data,how='left', on='player_id')
# print(auction_2012_data.head())

# def to_overseas(nationality):
#     if pd.isna(nationality):
#         return pd.NA
#     return nationality!='India'

# auction_2012_data['overseas'] = auction_2012_data['nationality'].apply(to_overseas)
# auction_2012_data.to_csv(out_dir / f"ipl_2012_auction.csv", index=False)

# print("rows:", len(auction_2012_data))
# print(auction_2012_data['overseas'].value_counts(dropna=False).to_string())


# INPUT_DIR2 = r'D:\DataEngineering\Final Year Project\processed_data\auction_data'
# in_dir2 = Path(INPUT_DIR2)
# YEARS_RANGE2 = [2008,2009,2010]
# SRC_COL2 = 'cost_usd'
# for year in YEARS_RANGE2:
#     f = in_dir2 / f"ipl_{year}_auction.csv"
#     print(f)
#     if not f.exists():
#         print(f"[skip] {f.name} not found")
#         continue
#     data = pd.read_csv(f)
#     # print(data['year'].head())
#     print(data['cost_usd'].dtype)
#     if SRC_COL2 not in data.columns:
#         print(f"[warn] {f.name}: no '{SRC_COL2}' column -> skipped (check its schema)")
#         continue
#     if year == 2008:
#         rate= 40
#     elif year == 2009:
#         rate = 48.7300
#     elif year == 2010:
#         rate = 45.8525
    
#     # print(rate)
#     data['sold_price'] = (data['cost_usd']*rate).round().astype('Int64')
#     data['sold_price_in_cr'] = data['sold_price']/10000000
    
#     data['base_price_in_inr'] = (data['base_price_in_usd']*rate).round().astype('Int64')
#     data['base_price_in_cr'] = data['base_price_in_inr']/10000000
    
#     print(f"[ok] {year}: {len(data):3d} rows | rate {rate} "
#             f"cr {data['sold_price_in_cr'].min():.2f}-{data['sold_price_in_cr'].max():.2f}")
#     print(data.head(10))
#     data.to_csv(out_dir / f"ipl_{year}_auction.csv", index=False)
 