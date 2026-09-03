"""
Add base price and a sold/unsold column to the auction file.
The new column is called `auction_result` (sold / unsold), because the auction
file already has a `status` column meaning something else (New / Retained / RTM).
"""

import pandas as pd

AUCTION_CSV  = r"D:\DataEngineering\Final Year Project\processed_data\new_auction_data\final_auction_all.csv"
PARSED_FILES = [r"D:\DataEngineering\Final Year Project\processed_data\unsold_data\unsold_with_base_price0_with_ids.csv",
                r"D:\DataEngineering\Final Year Project\processed_data\unsold_data\unsold_with_base_price1_with_ids.csv",
                r"D:\DataEngineering\Final Year Project\processed_data\unsold_data\unsold_with_base_price_2_with_ids.csv"]
OUTPUT_CSV   = r"D:\DataEngineering\Final Year Project\processed_data\new_auction_data\auction_all_with_base_price.csv"




auction = pd.read_csv(AUCTION_CSV)


auction["id_num"] = pd.to_numeric(auction["player_id"], errors="coerce")



pieces = []
for file_name in PARSED_FILES:
    page = pd.read_csv(file_name, dtype={"player_id": str})

    
    if "base_price" not in page.columns:
        page["base_price"] = pd.to_numeric(page["base_price_in_cr"], errors="coerce") * 10_000_000
    if "id_source" not in page.columns:
        page["id_source"] = ""
    if "base_price_in_usd" not in page.columns:
        page["base_price_in_usd"] = float("nan")

    pieces.append(page[["year", "player_name", "player_id","base_price_in_cr", "base_price", "base_price_in_usd","status", "id_source"]])

parsed = pd.concat(pieces, ignore_index=True)
parsed = parsed.rename(columns={"status": "auction_result"})

label = parsed["auction_result"].astype(str).str.strip().str.lower()
parsed["auction_result"] = "sold"
parsed.loc[label == "unsold", "auction_result"] = "unsold"


parsed["id_num"] = pd.to_numeric(parsed["player_id"], errors="coerce")



have_id = parsed[parsed["id_num"].notna()].drop_duplicates(["id_num", "year"])
no_id = parsed[parsed["id_num"].isna()]
parsed = pd.concat([have_id, no_id], ignore_index=True)



base_prices = parsed[["id_num", "year",
                      "base_price_in_cr", "base_price", "base_price_in_usd"]].dropna(subset=["id_num"])
base_prices = base_prices.rename(columns={"base_price_in_cr":  "unsold_cr",
                                        "base_price":        "unsold_full",
                                        "base_price_in_usd": "unsold_usd"})

full = auction.merge(base_prices, on=["id_num", "year"], how="left")


full["base_price"]        = full["base_price"].fillna(full["unsold_full"])
full["base_price_in_cr"]  = full["base_price_in_cr"].fillna(full["unsold_cr"])
full["base_price_in_usd"] = full["base_price_in_usd"].fillna(full["unsold_usd"])
full = full.drop(columns=["unsold_cr", "unsold_full", "unsold_usd"])


full["auction_result"] = "sold"
status_lc = full["status"].astype(str).str.strip().str.lower()
is_retained    = status_lc.isin(["retained", "rtm"])
is_transferred = full["transferred"] == 1
full.loc[is_retained | is_transferred, "auction_result"] = float("nan")
full["id_source"] = "from auction file"



auction_keys = auction[["id_num", "year"]].dropna().drop_duplicates()

check = parsed.merge(auction_keys, on=["id_num", "year"], how="left", indicator=True)
extra = parsed[check["_merge"] == "left_only"]

full = pd.concat([full, extra], ignore_index=True)
full = full.drop(columns=["id_num"])
full.to_csv(OUTPUT_CSV, index=False)


kept = (full["id_source"] == "from auction file").sum()
print("auction rows in :", len(auction))
print("kept in output  :", kept, "OK - none lost" if kept == len(auction) else "PROBLEM")
print("got a base price:", int(full.loc[full["id_source"] == "from auction file", "base_price_in_cr"].notna().sum()))
print("players added   :", len(extra))
print("TOTAL           :", len(full), "rows ->", OUTPUT_CSV)
print()
print(full["auction_result"].value_counts().to_string())