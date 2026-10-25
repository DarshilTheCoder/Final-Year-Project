# 🏏 What Drives an IPL Auction Price?

**Final Year Project: an end-to-end data science pipeline that collects, cleans and models 19 years of IPL auction data (2008–2026) to explain and predict how much franchises pay for a player.**

The project starts with web scraping and ends with statistical and machine-learning models. Along the way it combines auction results with each player's IPL performance from the **previous** season, so the models only use information franchises actually had on auction day.

---

## 📌 At a Glance

| | |
|---|---|
| **Auctions covered** | 19 (2008 → 2026), including 6 mega auctions |
| **Final dataset** | 4,028 player-auction records × 68 features, 1,110 unique players |
| **Sold with a price** | 1,644 players (1,104 used for modelling after removing missing core features) |
| **Target** | `log(sold_price)`. Raw prices are heavily right-skewed (skew 2.87 → 0.06 after log). |
| **Models** | Mean baseline, season baseline, base-price model, hedonic OLS, z-score OLS, Random Forest |
| **Validation** | Random 80/20 split, temporal holdout (train ≤ 2022 → test 2023–26), leave-one-year-out |
| **Best result** | Random Forest: **R² ≈ 0.52** on unseen auctions (2023–26); average **R² ≈ 0.40** across leave-one-year-out folds |

---

## 🔍 Key Findings

- **Base price is the strongest single signal.** It has a correlation of r = 0.67 with log price and accounts for about 49% of the Random Forest's feature importance.
- **International (capped) status matters most among categorical features.** It explains about 36% of the variance in log price (η² = 0.36, one-way ANOVA).
- **Recent IPL experience counts.** Whether a player played the previous IPL season explains about 17% of the variance (η² = 0.17).
- **Playing role on its own is a weak predictor** (η² ≈ 0.01–0.02). How well a player performs matters more than which role he plays.
- **Prices are noisy and season-dependent.** Residuals are heteroskedastic (Breusch–Pagan p < 1e-10), so coefficient tables use HC3 robust standard errors.
- **Model residuals show possible over- and underpayment.** Players paid far above or below what the model predicts for comparable players are listed at the end of the modelling notebook.

![Log sold price by auction outcome](processed_data/images/log_sold_price%20vs%20outcome.png)

---

## 📊 Model Results

R² is measured on held-out data, using the log of the sold price.

| Model | Random split | Temporal holdout (2023–26) | Leave-one-year-out (avg) |
|---|---:|---:|---:|
| Mean only (null) | −0.003 | −0.016 | −0.086 |
| Season only | 0.089 | −0.024 | −0.177 |
| Base price + season | 0.431 | 0.491 | 0.128 |
| Hedonic OLS | 0.435 | 0.493 | 0.298 |
| Z-score OLS (performance relative to role and year) | 0.507 | 0.508 | 0.288 |
| Random Forest (raw stats) | 0.509 | **0.516** | 0.390 |
| Random Forest (z-score features) | **0.516** | 0.464 | **0.401** |

RMSE on the log scale falls from **1.33** (null) to about **0.92–0.95** for the best models.

**Why three validation schemes?** A random split can mix seasons, so a model may see an auction's own price level during training. The temporal holdout and leave-one-year-out schemes test whether a model generalises to an auction it has never seen. That is the real use case.

---

## 🛠️ Pipeline

```
ESPNcricinfo ──► Scrape (Selenium) ──► Parse HTML (BeautifulSoup) ──► Combine & clean
                                                                              │
     Models ◄── EDA ◄── Feature engineering ◄── Lagged merge (leakage guard) ◄┘
```

1. **Scraping.** `undetected_chromedriver` + Selenium collect player profile pages for every franchise (CSK, MI, RCB, KKR, … including defunct teams such as Deccan Chargers, Kochi and Pune Warriors) and the auction result pages for each year.
2. **Parsing.** Auction pages changed format several times between 2008 and 2026, so each format has its own parser (2011/13, 2012, 2014, 2015, 2016, 2017–24, 2025–26). The 2008 data comes from Kaggle, and 2009–2010 were built manually because no clean source exists.
3. **Combining and cleaning.** Team files are merged, duplicate `(player_id, year)` rows are removed, dates are normalised, and best-bowling figures (`bbi`/`bbm`) are split into wickets and runs.
4. **Unsold players and base prices.** Sold/unsold lists are scraped separately. Missing player IDs are filled by **name matching**: first an exact match, then first initial + surname. Names that match more than one player are flagged as *ambiguous* rather than guessed, and every filled ID records how it was matched in `id_source`.
5. **Lagged merge (the leakage guard).** Each auction in year *N* is joined only with the player's stats from season *N − 1*. Built-in checks confirm that no rows are duplicated and that the lag is exactly one year.
6. **Feature engineering.** Adds `is_mega_auction`, `is_capped` (as of the auction year), `age_during_auction`, overseas status, consistent outcome labels (sold / unsold / retained / transferred) and standardised team names.
7. **EDA** (`eda_ipl_auction.ipynb`). Price distributions, outcomes by year, sold vs unsold profiles, ANOVA tests that justify grouping player roles, a correlation heatmap and a missing-data audit.
8. **Modelling** (`final_ML_modeling.ipynb`). Multicollinearity checks (correlation + VIF), baseline models, hedonic OLS, z-scored performance features, Random Forest, three validation schemes, residual diagnostics and a ranking of over- and undervalued players.

---

## 🗂️ Repository Structure

```
Final-Year-Project/
│
├── raw_data/
│   ├── auction_csv_data/        # One raw CSV per auction year (2008–2026)
│   └── players_csv_data/        # Raw per-franchise player stats from parsed HTML
│
├── processed_data/
│   ├── auction_data/            # Cleaned per-year auction files
│   ├── players_data/            # Cleaned per-franchise player stats
│   ├── unsold_data/             # Unsold players + base prices (with matched IDs)
│   ├── images/                  # Saved EDA figures
│   ├── final_auction_all.csv                       # All auctions combined
│   ├── auction_all_with_base_price.csv             # + base price & sold/unsold label
│   ├── final_4_with_status_auction_with_prior_stats.csv  # + lagged prior-season stats
│   └── final_4_modelling_ready_dataset.csv         # ✅ Final modelling dataset
│
├── pythoncodes/                 # All scraping, parsing, cleaning & modelling code
│   ├── eda_ipl_auction.ipynb
│   └── final_ML_modeling.ipynb
│
├── previously_created_datas/    # Earlier iterations of intermediate datasets (archive)
├── testing_folders/             # Scratch work and experiments
└── requirement.txt
```

### Scripts, in pipeline order

| Stage | Script(s) | Purpose |
|---|---|---|
| Scrape players | `team_scrapper.py`, `player_scrapper.py` | Collect player links per franchise, then save each player's profile page |
| Parse players | `html_parser.py`, `html_parser2.py`, `skipped_players.py` | Extract bio + season-by-season IPL batting/bowling stats into CSVs |
| Combine players | `player_data_combining.py` | Merge team files, deduplicate, clean dates and numeric fields |
| Scrape auctions | `auction_scrapper_17_24.py`, `auction_scrapper_25_26.py` | Download auction result pages |
| Parse auctions | `auction_11_13.py`, `auction_12.py`, `auction_14.py`, `auction_15.py`, `auction_16.py`, `auction_17_24.py`, `auction_25_26.py` | One parser per page format |
| Clean auctions | `auctiondata_transformation.py`, `combine_auction.py` | Standardise columns and currency (₹ crore), combine all years |
| Unsold + base price | `unsold_players_scrapper_1.py`, `unsold_players_scrapper_2.py`, `unsold_players_htmlparser0/1/2.py` | Scrape and parse sold/unsold lists with base prices |
| ID matching | `unsold_players_id_matching.py` | Fill missing player IDs by name matching, with an audit trail |
| Merge | `combine_with_baseprice.py`, `players_auction_datamerging.py` | Add base price and outcome, then run the lagged stats join |
| Features | `players_auction_data_transformation.py` | Build the modelling-ready dataset |
| Validate | `data_checking.py` | Sanity-check the auction ↔ stats merge and ID-matching sources |
| Analyse | `eda_ipl_auction.ipynb`, `final_ML_modeling.ipynb` | EDA and modelling |

---

## 📋 Key Features in the Final Dataset

| Feature | Description |
|---|---|
| `sold_price`, `sold_price_in_cr` | Final auction price (target, modelled as `log_price`) |
| `base_price`, `base_price_in_cr` | Player's reserve price at auction |
| `auction_result` | sold / unsold / retained / transferred |
| `is_capped` | Had the player played international cricket by the auction year? |
| `new_overseas` | Overseas player flag (filled from nationality where missing) |
| `age_during_auction` | Auction year − birth year |
| `intl_experience` | Years since international debut |
| `has_prior_season` | Did the player play the previous IPL season? |
| `is_mega_auction` | 2008, 2011, 2014, 2018, 2022, 2025 |
| `player_role` | Grouped into Batsman / Bowler / Allrounder / Wicketkeeper (chosen using ANOVA) |
| Prior-season stats | `matches`, `runs`, `batting_average`, `batting_strikerate`, `wickets`, `economy`, `bowl_ave`, `bbi_wkts`, … |

---

## 🚀 Getting Started

### 1. Install dependencies

`requirement.txt` currently lists only the core packages. The full project also needs:

```bash
pip install numpy pandas scipy matplotlib scikit-learn statsmodels \
            beautifulsoup4 selenium undetected-chromedriver
```

### 2. Explore or reproduce the models (recommended)

You don't need to re-scrape anything. The cleaned dataset is already in the repo.

1. Open `pythoncodes/eda_ipl_auction.ipynb` or `pythoncodes/final_ML_modeling.ipynb` (both were run in Google Colab).
2. Point `DATA_PATH` / `path` at `processed_data/final_modelling_ready_dataset.csv`. The notebooks currently use the Colab path `/content/...`.
3. Run all cells.

### 3. Rebuild the dataset from scratch (optional)

Run the scripts in the order shown in the table above. Notes:
- Several scripts use **hardcoded absolute paths** (e.g. `D:\DataEngineering\...`). Update `INPUT_DIR` / `OUTPUT_DIR` / `RAW_DIR` at the top of each script.
- Scrapers need Google Chrome. `version_main=149` in the scrapers must match your installed Chrome version.
- Raw HTML pages are excluded from the repo via `.gitignore` because of their size, so scraping must be re-run to regenerate them.

---

## ⚠️ Limitations

- **Debutants have no prior IPL stats**, so performance features are missing for players without a previous season. This is captured with `has_prior_season`.
- **Early auctions are sparse.** 2008–2010 come from Kaggle or manual entry, and some years lack base prices.
- **The Random Forest overfits somewhat** (train R² ≈ 0.91 vs test ≈ 0.51). Hyperparameter tuning is a natural next step.
- **Auction dynamics aren't captured.** Bidding wars, franchise purse strategy and team needs drive much of the remaining unexplained variance.

---

## 🧰 Tech Stack

**Python** · pandas · NumPy · BeautifulSoup · Selenium (undetected-chromedriver) · SciPy · statsmodels · scikit-learn · Matplotlib · Jupyter / Google Colab

---

## 📄 Data Source & Usage

Player statistics and auction results were collected from **ESPNcricinfo** for academic, non-commercial research. The 2008 auction data comes from Kaggle. Please respect the source websites' terms of use if you re-run the scrapers.

**Author:** Darshil Parikh
