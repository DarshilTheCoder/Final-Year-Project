import glob
import numpy as np
import pandas as pd
from pathlib import Path

# ---- EDIT THESE ----------------------------------------------------------
# Folder that holds the *_players_data.csv team files (NOT your code folder).
INPUT_DIR  = r"D:\DataEngineering\Final Year Project\processed_data\players_data"
OUTPUT_DIR = r"D:\DataEngineering\Final Year Project\processed_data\players_data"
# --------------------------------------------------------------------------

# ============================ stats cleaning ==============================
MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")
NUMERIC = ["matches", "innings", "no", "runs", "highestscore", "batting_average",
           "bf", "strikerate", "100s", "50s", "4s", "6s", "Ct", "St", "wickets",
           "economy", "balls", "bowl_ave", "sr", "4w", "5w", "10w"]
DATES = ["birthdate", "t20_start", "t20_end", "odi_start", "odi_end"]


def parse_dateish(series):
    """Pull 'Month DD, YYYY' from anywhere (clean dates OR full match
    descriptions) and return it as YYYY-MM-DD."""
    ext = series.str.extract(rf"({MONTHS})\s+(\d{{1,2}})(?:\s*-\s*\d{{1,2}})?,?\s+(\d{{4}})")
    combo = ext[0] + " " + ext[1] + ", " + ext[2]
    return pd.to_datetime(combo, format="%B %d, %Y", errors="coerce").dt.strftime("%Y-%m-%d")


def clean_stats(s):
    s = s.replace(r"^\s*-\s*$", np.nan, regex=True)          # "-"  -> empty
    s["highestscore"] = s["highestscore"].str.replace("*", "", regex=False)  # drop the *

    # bbi/bbm: KEEP the readable "4/17" string, and ALSO add numeric wkts/runs
    # for the model. (Want string only? delete these 4 lines. Want numbers only?
    # keep them and add:  s = s.drop(columns=["bbi", "bbm"]) )
    for col in ["bbi", "bbm"]:
        parts = s[col].str.split("/", expand=True)
        s[f"{col}_wkts"] = pd.to_numeric(parts[0], errors="coerce")
        s[f"{col}_runs"] = pd.to_numeric(parts[1], errors="coerce")

    for col in DATES:                                        # dates only, ISO format
        s[col] = parse_dateish(s[col])
    for col in NUMERIC:                                      # text -> real numbers
        s[col] = pd.to_numeric(s[col], errors="coerce")
    return s


# ======================= combine the 15 team files ========================
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

# 3. dedup player-seasons (a player at multiple franchises appears in multiple files)
players = (players
        .drop_duplicates(subset=['player_id', 'year'], keep='first')
        .reset_index(drop=True))
print(f"After dedup: {len(players)} player-seasons, {players['player_id'].nunique()} players")

# 4. clean, then tidy the id column
players = clean_stats(players)
players['player_id'] = pd.to_numeric(players['player_id'], errors='coerce').astype('Int64')

out_dir = Path(OUTPUT_DIR)
out_dir.mkdir(parents=True, exist_ok=True)
players.to_csv(out_dir / 'new_all_players_combined.csv', index=False)
print(f"Cleaned & saved -> {out_dir / 'new_all_players_combined.csv'}")