"""
GROUP C parser  ->  2025, 2026
To parse the unsold players from the HTML pages downloaded from the IPL website.
"""

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


PAGES_DIR  = r"D:\DataEngineering\Final Year Project\pythoncodes\data\unsold_page2"
OUTPUT_CSV = r"D:\DataEngineering\Final Year Project\pythoncodes\data\unsold_page2/unsold_with_base_price_2.csv"
YEARS      = [2025, 2026]


def get_year(filename):
    return int(re.search(r"(20\d\d)", filename).group(1))

def get_player_id(href):
    if not href:
        return None
    m = re.search(r"-(\d+)$", href.rstrip("/"))
    return int(m.group(1)) if m else None


def to_number(value):
    try:
        return float(value)
    except ValueError:
        return None


rows = []
for path in sorted(Path(PAGES_DIR).glob("*.html")):
    year = get_year(path.name)
    if year not in YEARS:
        continue

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    table = soup.find("table", class_="ds-table")

    for row in table.select("tbody tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) < 3:
            continue                            

        link = row.find("a", href=True)
        rows.append({
            "year": year,
            "player_name": cells[0],               
            "player_id": get_player_id(link["href"] if link else None),
            "base_price_in_cr": to_number(cells[1]),  
            "status": "unsold" if cells[2].lower() == "unsold" else "sold",
            "source_text": " | ".join(cells),
        })

players = pd.DataFrame(rows)
players.to_csv(OUTPUT_CSV, index=False)

print(f"{len(players)} rows -> {OUTPUT_CSV}\n")
summary = players.groupby(["year", "status"]).agg(
    players=("player_name", "size"),
    with_id=("player_id", "count"),
    with_base_price=("base_price_in_cr", "count"))
print(summary.to_string())