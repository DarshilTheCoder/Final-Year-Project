"""
GROUP A parser  ->  2015, 2017, 2018, 2019, 2020, 2021, 2024

These pages use the layout:   <div class="Article">
One player per element, e.g.
    Ben Stokes (Base price INR 2 crore) - Sold to Rising Pune Supergiants ...
Base prices here are always in INR (2015 has none at all).

Output: base_prices_group_a.csv
"""

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

# ---- EDIT THESE ----------------------------------------------------------
PAGES_DIR  = r"D:\DataEngineering\Final Year Project\pythoncodes\data\unsold_page0"
OUTPUT_CSV = r"D:\DataEngineering\Final Year Project\pythoncodes\data\unsold_page0/unsold_with_base_price0.csv"
YEARS      = [2015, 2017, 2018, 2019, 2020, 2021, 2024]
# --------------------------------------------------------------------------


def get_year(filename):
    return int(re.search(r"(20\d\d)", filename).group(1))


def get_player_id(href):
    """The id is the number in the player link. Two link shapes exist:
         .../content/player/43906.html   -> 43906
         .../cricketers/karun-nair-398439 -> 398439
    """
    if not href:
        return None
    m = re.search(r"/player/(\d+)\.html", href) or re.search(r"-(\d+)$", href.rstrip("/"))
    return int(m.group(1)) if m else None


def get_base_price(text):
    """'(Base price INR 1.5 crore)' -> 1.5 crore.  Returns crores.
    2021 spells lakh as 'lac', so all three spellings are allowed."""
    m = re.search(r"base price\s*(?:INR|Rs\.?)?\s*([\d.]+)\s*(crore|lakh|lac)", text, re.I)
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2).lower()
    return value if unit.startswith("crore") else value / 100      # 100 lakh = 1 crore


def get_name(element, text):
    """Prefer the player link, then bold text, then the words before ' -' / ' ('."""
    link = element.find("a", href=True)
    if link and re.search(r"/player/|/cricketers/", link["href"]):
        return link.get_text(" ", strip=True)
    bold = element.find("b")
    if bold and bold.get_text(strip=True):
        return bold.get_text(" ", strip=True)
    return re.split(r"\s+[-(]", text)[0].strip()


rows = []
for path in sorted(Path(PAGES_DIR).glob("*.html")):
    year = get_year(path.name)
    if year not in YEARS:
        continue

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    body = soup.find("div", class_="Article")
    section = None                      # 'sold' or 'unsold', set by the headings

    for element in body.find_all(["h2", "p"]):
        text = re.sub(r"\s+", " ", element.get_text(" ", strip=True))
        if not text:
            continue

        # Is this a section heading? Headings are short, have no player link and
        # no price text. We must check that, because in 2015 and 2017 some
        # PLAYER lines are <h2> tags too - the tag alone tells us nothing.
        is_heading = (len(text) < 60
                      and not element.find("a", href=True)
                      and not re.search(r"base price|sold to|crore|lakh|lac", text, re.I))
        if is_heading:
            if "unsold" in text.lower():
                section = "unsold"          # test 'unsold' BEFORE 'sold'
            elif "sold" in text.lower():
                section = "sold"
            continue

        if section is None:
            continue

        # Skip the two kinds of non-player text that sit inside these sections:
        #   "INR 1 crore = INR 100 lakh = ..."   the currency-conversion note
        #   "(Players who were signed ...)"      a bracketed explanation
        if text.startswith("(") or " = " in text:
            continue                        # intro text before the first heading

        link = element.find("a", href=True)
        rows.append({
            "year": year,
            "player_name": get_name(element, text),
            "player_id": get_player_id(link["href"] if link else None),
            "base_price_in_cr": get_base_price(text),
            "status": section,
            "source_text": text[:160],
        })

players = pd.DataFrame(rows)
players.to_csv(OUTPUT_CSV, index=False)

print(f"{len(players)} rows -> {OUTPUT_CSV}\n")
summary = players.groupby(["year", "status"]).agg(
    players=("player_name", "size"),
    with_id=("player_id", "count"),
    with_base_price=("base_price_in_cr", "count"))
print(summary.to_string())