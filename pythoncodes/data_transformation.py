

import pandas as pd
from pathlib import Path

# ---- EDIT THESE ----------------------------------------------------------
INPUT_DIR  = r"D:\DataEngineering\Final Year Project\processed_data"       # folder holding ipl_YYYY_auction.csv
OUTPUT_DIR = r"D:\DataEngineering\Final Year Project\processed_data\new_auction_data"       # where to write (same folder is fine)
YEARS      = range(2017, 2025)             # 2017..2024 inclusive
SRC_COL    = "cost_inr_lakh"               # raw price column (in lakhs)
# --------------------------------------------------------------------------

in_dir, out_dir = Path(INPUT_DIR), Path(OUTPUT_DIR)
out_dir.mkdir(parents=True, exist_ok=True)

for year in YEARS:
    f = in_dir / f"ipl_{year}_auction.csv"
    if not f.exists():
        print(f"[skip] {f.name} not found")
        continue

    df = pd.read_csv(f)
    if SRC_COL not in df.columns:
        print(f"[warn] {f.name}: no '{SRC_COL}' column -> skipped (check its schema)")
        continue

    lakh = pd.to_numeric(df[SRC_COL], errors="coerce")     # NaN-safe
    df["sold_price_in_cr"] = lakh / 100                    # crores (float)
    df["sold_price"]       = (lakh * 100_000).round().astype("Int64")  # full INR

    # quick per-file sanity line (verify-as-you-go)
    print(f"[ok] {year}: {len(df):3d} rows | "
          f"cr {df['sold_price_in_cr'].min():.2f}-{df['sold_price_in_cr'].max():.2f} | "
          f"missing price: {int(lakh.isna().sum())}")
    df.to_csv(out_dir / f"ipl_{year}_auction.csv", index=False)



print("\nDone. Spot-check one file before trusting the batch.")