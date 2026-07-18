"""
Combine all IPL auction files (2008-2026) into one table, keeping only the
columns that exist in every file: player_id, player_name, team, and the sold
price (full rupees + crores). `year` is added so rows stay distinguishable.

Different years name the same column differently, so we rename to one set first.
"""

import re
import pandas as pd
from pathlib import Path

# ---- EDIT THESE ----------------------------------------------------------
INPUT_DIR  = r"D:\DataEngineering\Final Year Project\processed_data\auction_data"        # folder with ipl_YYYY_auction.csv
OUTPUT_DIR = r"D:\DataEngineering\Final Year Project\processed_data\auction_data"  # where auction_all.csv is written
# --------------------------------------------------------------------------

# variant column names  ->  the single name we want
RENAME = {
    "id": "player_id",
    "name": "player_name", "Player": "player_name",
    "team_name": "team", "Team": "team", "Franchise (Team)": "team",
}

def purse_to_cr(series):
    """Purse in crores. Handles 'X cr' strings and raw-rupee integers alike."""
    nums = pd.to_numeric(series.astype(str).str.replace(r"[^\d.]", "", regex=True),
                         errors="coerce")
    if nums.notna().any() and nums.median() > 1e4:   # values are raw rupees, not cr
        nums = nums / 1e7
    return nums

frames = []
for path in sorted(Path(INPUT_DIR).glob("ipl_*_auction.csv")):
    year = int(re.search(r"ipl_(\d{4})", path.name).group(1))
    df = pd.read_csv(path).rename(columns=RENAME)

    # 2014 stores the price in lakhs (cost_inr_lakh) instead of sold_price
    if "sold_price" not in df.columns:
        df["sold_price"] = pd.to_numeric(df["cost_inr_lakh"], errors="coerce") * 100_000

    df["year"] = year
    df["sold_price"] = pd.to_numeric(df["sold_price"], errors="coerce")
    df["sold_price_in_cr"] = df["sold_price"] / 10_000_000        # 1 crore = 1e7 rupees
    
    if year >= 2017:
        df["purse_spent_in_cr"] = purse_to_cr(df["purse_spent"])
        df["purse_left_in_cr"]  = purse_to_cr(df["purse_left"])
        # df['status'] = df['status']
        # df['transferred'] = df['transferred']
        # df['overseas'] = df['overseas']
    else:
        df["purse_spent_in_cr"] = float("nan")
        df["purse_left_in_cr"]  = float("nan")
        df['status'] = float('nan')
        df['transferred'] = float('nan')
        df['overseas'] = float('nan')
    df["purse_spent"] = df["purse_spent_in_cr"] * 10_000_000      # back to full rupees
    df["purse_left"]  = df["purse_left_in_cr"]  * 10_000_000

    frames.append(df[["year", "player_id", "player_name", "team",
                      "sold_price", "sold_price_in_cr","purse_spent", "purse_spent_in_cr",
                      "purse_left", "purse_left_in_cr",'status','transferred','overseas']])

auction = pd.concat(frames, ignore_index=True)
auction = auction.dropna(subset=["player_name"])                 # drop any blank rows
auction["player_id"] = pd.to_numeric(auction["player_id"], errors="coerce").astype("Int64")
auction["sold_price"] = auction["sold_price"].round().astype("Int64")
auction = auction.sort_values(["year", "team", "player_name"]).reset_index(drop=True)

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
auction.to_csv(Path(OUTPUT_DIR) / "with_status_auction_all.csv", index=False)

print(f"{len(auction)} rows, years {auction.year.min()}-{auction.year.max()}")
print("rows with no sold price:", int(auction.sold_price.isna().sum()))
print("years with purse filled:", sorted(auction.loc[auction.purse_spent_in_cr.notna(), "year"].unique()))