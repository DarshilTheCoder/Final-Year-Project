"""player_data_combining file is used to to combine all team players data which then get stored inside the players_data folder inside the processed data, as it was the data processed and extracted from the raw html pages. Also, aftetr combining all players I tried to do bit of data transformation and cleaning in-order to get proper combined_players_data """

import glob
import numpy as np
import pandas as pd
from pathlib import Path


INPUT_DIR  = r"/Users/umerkarachiwala/Desktop/Darshil'sFinalYearProject/Final-Year-Project/processed_data/players_data"
OUTPUT_DIR = r"/Users/umerkarachiwala/Desktop/Darshil'sFinalYearProject/Final-Year-Project/processed_data/players_data"



MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December")
NUMERIC = ["matches", "innings", "no", "runs", "highestscore", "batting_average","bf", "strikerate", "100s", "50s", "4s", "6s", "Ct", "St", "wickets","economy", "balls", "bowl_ave", "sr", "4w", "5w", "10w"]
DATES = ["birthdate", "t20_start", "t20_end", "odi_start", "odi_end"]

#this funciton is used to extract the date from the players csv file, example t20 start date, end date, birthdate. This function is also written with the help of an AI, as it was difficult to extract dates from string
def parse_date(series):
    """Pull 'Month DD, YYYY' from anywhere (clean dates OR full match
    descriptions) and return it as YYYY-MM-DD."""
    ext = series.str.extract(rf"({MONTHS})\s+(\d{{1,2}})(?:\s*-\s*\d{{1,2}})?,?\s+(\d{{4}})")
    combo = ext[0] + " " + ext[1] + ", " + ext[2]
    new_date = pd.to_datetime(combo, format="%B %d, %Y", errors="coerce").dt.strftime("%Y-%m-%d")
    return new_date

#clean_stats is the function which do some basic cleaning before after like replace '-' with empty cell, then removing * mark from highest score, otherwise it becomes a string
def clean_stats(s):
    s = s.replace(r"^\s*-\s*$", np.nan, regex=True)         
    s["highestscore"] = s["highestscore"].str.replace("*", "", regex=False) 

    #bbi/bbm are the best bowling figures (i.e wickets/run) for an inning(bbi) and for a match(bbm), but it gets converted into date format in the excel, so I just split them into wickets and runs. As for T20 matches or IPL type leagues both bbi and bbm are same. 
    for col in ["bbi", "bbm"]:
        parts = s[col].str.split("/", expand=True)
        s[f"{col}_wkts"] = pd.to_numeric(parts[0], errors="coerce")
        s[f"{col}_runs"] = pd.to_numeric(parts[1], errors="coerce")

    for col in DATES:                                    
        s[col] = parse_date(s[col])
    for col in NUMERIC:
        s[col] = pd.to_numeric(s[col], errors="coerce")
    return s


in_dir = Path(INPUT_DIR)

# 1. gather the 15 team files from players_data (exclude the stray
#    ipl_players_data.csv; the combined output doesn't match the pattern)
team_files = sorted(f for f in in_dir.glob('*_players_[dD]ata.csv')
                    if not f.name.startswith('ipl'))
print(f"Combining {len(team_files)} team files from {in_dir}")
if not team_files:
    raise SystemExit("No *_players_data.csv files found - check INPUT_DIR.")

# 2. concat - read as text so cleaning sees raw values ("4/17", "62*", "-")
players = pd.concat([pd.read_csv(f, dtype=str) for f in team_files], ignore_index=True)
print(f"Raw combined rows: {len(players)}")


# check for duplicate (player_id, year) groups with conflicting values
dupe_keys = players[players.duplicated(['player_id','year'], keep=False)]
nun = dupe_keys.groupby(['player_id','year']).nunique(dropna=False)
conflict_cols = (nun > 1).sum().sort_values(ascending=False)
print("\nColumns where duplicate (player_id, year) groups disagree:")
print(conflict_cols[conflict_cols > 0].to_string())

# how many (player_id, year) duplicate groups have conflicting values?
dupe_keys = players[players.duplicated(['player_id','year'], keep=False)]
conflicts = (dupe_keys.groupby(['player_id','year']).nunique(dropna=False) > 1).any(axis=1).sum()
print("duplicate groups with conflicting values:", conflicts)


# 3. dedup player-seasons (a player at multiple franchises appears in multiple files)
before_rows    = len(players)
before_players = players['player_id'].nunique()

players = (players
        .drop_duplicates(subset=['player_id', 'year'], keep='first')
        .reset_index(drop=True))

after_rows    = len(players)
after_players = players['player_id'].nunique()

dedup_summary = pd.DataFrame(
    {"Count": [before_rows,
               before_players,
               before_rows - after_rows,
               after_rows,
               after_players]},
    index=["Total rows (before dedup)",
           "Unique players (before dedup)",
           "Duplicate rows dropped",
           "Remaining rows (after dedup)",
           "Unique players (after dedup)"],
)
print("\n--- Deduplication summary ---")
print(dedup_summary.to_string())
print()

# 4. clean, then tidy the id column
players = clean_stats(players)
players['player_id'] = pd.to_numeric(players['player_id'], errors='coerce').astype('Int64')

out_dir = Path(OUTPUT_DIR)
out_dir.mkdir(parents=True, exist_ok=True)
players.to_csv(out_dir / 'new_players_combined2.csv', index=False)
print(f"Cleaned & saved -> {out_dir / 'new_players_combined2.csv'}")