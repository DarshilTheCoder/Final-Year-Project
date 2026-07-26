"""
Fill the missing player_id in the unsold/base-price CSVs by matching names.

Reference names come from the merged auction file, which already has ids.

Two matching rules, tried in order:
  1. exact name after cleaning   "R Ashwin"  == "r ashwin"
  2. first initial + surname     "B Indrajith" -> ('b','indrajith')
     This catches "Adam Milne" vs the stats file's "Adam Fraser Milne".

A name that maps to MORE THAN ONE id is never filled automatically - it is
marked 'ambiguous' for you to decide. There really are different players with
the same name (two Amit Mishras, three V Singhs), so guessing would be wrong.

Every filled row records HOW it was filled in `id_source`, so the work is
auditable rather than magic.
"""

import re
from pathlib import Path

import pandas as pd

# ---- EDIT THESE ----------------------------------------------------------
UNSOLD_FILES = ["unsold_with_base_price_2.csv"]
AUCTION_CSV  = "fourth_with_status_auction_with_prior_stats.csv"
OUT_SUFFIX   = "_with_ids"
# --------------------------------------------------------------------------


def clean_name(name):
    """'M.S. Dhoni ' -> 'm s dhoni'  (lowercase, letters and spaces only)"""
    name = re.sub(r"[^a-z ]", " ", str(name).lower())
    return re.sub(r"\s+", " ", name).strip()


def initial_surname(name):
    """'R Ashwin' and 'Ravichandran Ashwin' both -> ('r', 'ashwin')"""
    parts = clean_name(name).split()
    return (parts[0][0], parts[-1]) if len(parts) >= 2 else None


# ---------- build the reference: every known name -> its id(s) -------------
reference = pd.read_csv(AUCTION_CSV)[["player_name", "player_id"]].dropna()
reference["player_id"] = reference["player_id"].astype(int)

by_name = reference.assign(k=reference.player_name.map(clean_name)) \
                   .groupby("k").player_id.unique()
by_initial = reference.assign(k=reference.player_name.map(initial_surname)) \
                      .dropna(subset=["k"]).groupby("k").player_id.unique()


def look_up(name):
    """-> (player_id, how_it_was_found). Never guesses between two players."""
    key = clean_name(name)
    if key in by_name.index:
        ids = by_name[key]
        return (ids[0], "name match") if len(ids) == 1 else (None, "ambiguous name")

    key = initial_surname(name)
    if key is not None and key in by_initial.index:
        ids = by_initial[key]
        return (ids[0], "initial match") if len(ids) == 1 else (None, "ambiguous initial")

    return None, "not found - add manually"


# ---------- fill each file ------------------------------------------------
for path in UNSOLD_FILES:
    players = pd.read_csv(path)
    players["id_source"] = ""

    for i, row in players.iterrows():
        if pd.notna(row["player_id"]):
            players.at[i, "id_source"] = "already had id"
            continue
        found_id, how = look_up(row["player_name"])
        if found_id is not None:
            players.at[i, "player_id"] = found_id
        players.at[i, "id_source"] = how

    players["player_id"] = players["player_id"].astype("Int64")   # keeps blanks blank
    out = Path(path).stem + OUT_SUFFIX + ".csv"
    players.to_csv(out, index=False)

    still_missing = int(players.player_id.isna().sum())
    print(f"{path}  ->  {out}")
    print(f"   {len(players)} rows | ids filled: {int(players.player_id.count())} | "
          f"still blank: {still_missing}")
    print(players.id_source.value_counts().to_string().replace("\n", "\n   ").rjust(3))
    print()

print("Rows marked 'ambiguous' or 'not found' are the ones to fill by hand.")
print("Filter on id_source in Excel to see just those.")