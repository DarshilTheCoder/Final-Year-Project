"""
Merge auction data with player stats using a LAGGED join:
auction year Y  <-  season (Y-1) stats.  This is the leakage guard: the auction
happens before the season, so only PRIOR-season performance may be a feature.

The stats 'year' is a cricket-season label. Three use slash format and are
mapped explicitly (a plain "take the second half" rule gets 2020 wrong, because
IPL 2020 was played in the 2020/21 season):
    2007/08 -> 2008 IPL    2009/10 -> 2010 IPL    2020/21 -> 2020 IPL

Output: auction_with_prior_stats.csv  (one row per auction row; stats columns
are NaN when the player has no prior-season record).  `has_prior_season` flags
matched vs not, so you can handle debutants/uncapped players explicitly.
"""

import re
import pandas as pd
from pathlib import Path

# ---- EDIT THESE ----------------------------------------------------------
AUCTION_CSV = r"D:\DataEngineering\Final Year Project\processed_data\auction_all_with_base_price.csv"
STATS_CSV   = r"D:\DataEngineering\Final Year Project\processed_data\new_players_combined.csv"
OUTPUT_DIR  = r"D:\DataEngineering\Final Year Project\processed_data"
# --------------------------------------------------------------------------

SEASON_LABEL = {"2007/08": 2008, "2009/10": 2010, "2020/21": 2020}


def to_season(y):
    """Season label -> integer IPL edition year."""
    y = str(y).strip()
    return SEASON_LABEL[y] if y in SEASON_LABEL else int(y)


auc = pd.read_csv(AUCTION_CSV)
stats = pd.read_csv(STATS_CSV, dtype={"year": str})

auc["player_id"]   = pd.to_numeric(auc["player_id"], errors="coerce")     # <-- add
stats["player_id"] = pd.to_numeric(stats["player_id"], errors="coerce")   # <-- add

stats["season"] = stats["year"].map(to_season)

# lagged left join: keep every auction row, attach season (Y-1) stats
auc["prior_season"] = auc["year"] - 1
merged = auc.merge(
    stats.drop(columns=["year"]),            # drop the string label; keep int season
    how="left",
    left_on=["player_id", "prior_season"],
    right_on=["player_id", "season"],
    suffixes=("", "_stats"),
)
merged["has_prior_season"] = merged["season"].notna()
merged = merged.drop(columns=["season"])     # == prior_season when matched; redundant

static_cols = ["nationality", "player_role", "batting_style", "bowling_style", "birthdate", "international_career","t20_start", "t20_end", "odi_start", "odi_end"]

player_static = stats.groupby("player_id")[static_cols].first().reset_index()  # first non-null per player

merged = merged.merge(player_static, on="player_id", how="left", suffixes=("", "_fill"))
for col in static_cols:
    merged[col] = merged[col].fillna(merged[col + "_fill"])   # only fill where the lagged join left it blank
    merged = merged.drop(columns=[col + "_fill"])

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
merged.to_csv(Path(OUTPUT_DIR) / "final_4_with_status_auction_with_prior_stats.csv", index=False)

# ======================= VERIFICATION =======================
m = merged["has_prior_season"]
print("1. rows preserved      :", len(auc), "->", len(merged),
      "OK" if len(merged) == len(auc) else "FAN-OUT (duplicate stats keys!)")
with_id = merged[merged["player_id"].notna()]
print("2. duplicate (id,year) :", int(with_id.duplicated(["player_id", "year"], keep=False).sum()),
      "(want 0)")
lag_ok = (merged.loc[m, "prior_season"] == merged.loc[m, "year"] - 1).all()
print("3. lag is exactly 1    :", bool(lag_ok), "(no same-year leakage)")
print(f"4. matched with stats  : {m.sum()}/{len(merged)} ({100*m.mean():.1f}%)")

print("\n   match rate by auction year (2008 = 0% is expected, no 2007 season):")
print(merged.assign(_m=m).groupby("year")["_m"].mean().mul(100).round().to_string())

print(f"\nWritten: {Path(OUTPUT_DIR) / 'auction_with_prior_stats.csv'}"
      f"  ({merged.shape[0]} rows x {merged.shape[1]} cols)")
print(f"After dedup: {len(merged)} player-seasons, {merged['player_id'].nunique()} players")