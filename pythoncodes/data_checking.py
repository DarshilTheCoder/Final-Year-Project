"""
Check the auction<->stats merge is correct.
Run this AFTER merge_auction_stats.py has produced auction_with_prior_stats.csv.
It loads the files from disk, so you can just run it - nothing to paste.
"""

import pandas as pd
from pathlib import Path

# ---- EDIT THESE ----------------------------------------------------------
AUCTION_CSV = r"D:\DataEngineering\Final Year Project\processed_data\auction_data\auction_all_with_base_price.csv"
MERGED_CSV  = r"D:\DataEngineering\Final Year Project\processed_data\final_with_status_auction_with_prior_stats.csv"
# --------------------------------------------------------------------------

auc = pd.read_csv(AUCTION_CSV)
m = pd.read_csv(MERGED_CSV)
has = m["has_prior_season"] == True

print("=" * 60)
print("STRUCTURAL CHECKS (automatic - these should all say OK)")
print("=" * 60)

# 1. no rows gained or lost
print(f"1. rows: auction={len(auc)}  merged={len(m)}  ->",
      "OK" if len(m) == len(auc) else "PROBLEM: rows changed (stats had duplicate keys)")

# 2. still one row per player per auction
d = int(m.duplicated(["player_id", "year"], keep=False).sum())
print(f"2. duplicate (player_id, year) rows: {d}  ->",
      "OK" if d == 0 else "PROBLEM: same player appears twice in a year")

# 3. attached season is always exactly one year before the auction
lag_ok = (m.loc[has, "prior_season"] == m.loc[has, "year"] - 1).all()
print(f"3. every matched row has prior_season == year-1  ->",
      "OK (no leakage)" if lag_ok else "PROBLEM: wrong season attached")

# 4. how many rows got stats (informational, not pass/fail)
print(f"4. rows with prior-season stats: {has.sum()}/{len(m)} ({100*has.mean():.0f}%)"
      f"   [the rest are debutants/uncapped - expected]")

print("\n" + "=" * 60)
print("MANUAL SPOT-CHECK (eyeball these, then verify on ESPNcricinfo)")
print("=" * 60)
print("For each player: 'lag' must be 1, and the runs/wickets should match")
print("that player's REAL IPL stats for the 'prior_season' shown.\n")

# pick some well-known players and show their attached prior-season line
famous = ["Kohli", "Rohit", "Dhoni", "Rayudu", "Jadeja",
          "Bumrah", "Warner", "Russell", "Rashid", "Buttler"]
m["lag"] = m["year"] - m["prior_season"]
cols = ["player_name", "year", "prior_season", "lag",
        "matches", "runs", "wickets", "team_stats"]
rows = [m[has & m["player_name"].str.contains(n, case=False, na=False)][cols].head(1)
        for n in famous]
rows = [r for r in rows if len(r)]
if rows:
    print(pd.concat(rows, ignore_index=True).to_string(index=False))