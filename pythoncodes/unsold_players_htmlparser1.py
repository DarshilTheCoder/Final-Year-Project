"""
GROUP B parser  ->  2012, 2013, 2016, 2022, 2023
To parse the unsold players from the HTML pages downloaded from the IPL website.
"""

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


PAGES_DIR  = r"D:\DataEngineering\Final Year Project\pythoncodes\data\unsold_page1"
OUTPUT_CSV = r"D:\DataEngineering\Final Year Project\pythoncodes\data\unsold_page1/unsold_with_base_price1.csv"
YEARS      = [2012, 2013, 2016, 2022, 2023]



def get_year(filename):
    return int(re.search(r"(20\d\d)", filename).group(1))

def get_player_id(href):
    if not href:
        return None
    m = re.search(r"/player/(\d+)\.html", href) or re.search(r"-(\d+)$", href.rstrip("/"))
    return int(m.group(1)) if m else None

def get_base_price(text):
    m = re.search(r"base price\s*(?:INR|INt|Rs\.?)?\s*([\d.]+)\s*(crore|lakh|lac)", text, re.I)
    if m:
        value, unit = float(m.group(1)), m.group(2).lower()
        return (value if unit.startswith("crore") else value / 100), None

    m = re.search(r"base price\s*\$\s*([\d,]+)", text, re.I)          
    if m:
        return None, float(m.group(1).replace(",", ""))

    if not re.search(r"crore|lakh|lac", text, re.I):                  
        m = re.search(r"base price\s*([\d,]{4,})", text, re.I)
        if m:
            return None, float(m.group(1).replace(",", ""))
    return None, None


def get_name(piece, text):
    link = piece.find("a", href=True)
    if link and re.search(r"/player/|/cricketers/", link["href"]):
        return link.get_text(" ", strip=True)
    bold = piece.find("b")
    if bold and bold.get_text(strip=True):
        return bold.get_text(" ", strip=True)
    return re.split(r"\s+[-(]", text)[0].strip()


rows = []
for path in sorted(Path(PAGES_DIR).glob("*.html")):
    year = get_year(path.name)
    if year not in YEARS:
        continue

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    body = soup.find("article", class_="ci-story")
    section = None

    for element in body.find_all(["h2", "p"]):
        whole_text = re.sub(r"\s+", " ", element.get_text(" ", strip=True))
        if not whole_text:
            continue

        is_heading = (len(whole_text) < 60
                      and not element.find("a", href=True)
                      and not re.search(r"base price|sold to|crore|lakh|lac|\$", whole_text, re.I))
        if is_heading:
            low = whole_text.lower()
            for word in ("unsold", "sold", "bought", "retained", "transferred"):
                if word in low:
                    section = word
                    break
            continue

        if section is None:
            continue
        for chunk in re.split(r"<br\s*/?>", str(element)):
            piece = BeautifulSoup(chunk, "html.parser")
            text = re.sub(r"\s+", " ", piece.get_text(" ", strip=True))
            if not text:
                continue

            if text.startswith("(") or " = " in text:
                continue

            name = get_name(piece, text)
            if len(name) > 40:                  
                continue

            in_cr, usd = get_base_price(text)
            link = piece.find("a", href=True)
            rows.append({
                "year": year,
                "player_name": name,
                "player_id": get_player_id(link["href"] if link else None),
                "base_price_in_cr": in_cr,
                "base_price_usd": usd,
                "status": section,
                "source_text": text[:160],
            })

players = pd.DataFrame(rows)
players.to_csv(OUTPUT_CSV, index=False)

print(f"{len(players)} rows -> {OUTPUT_CSV}\n")
summary = players.groupby(["year", "status"]).agg(
    players=("player_name", "size"),
    with_id=("player_id", "count"),
    base_inr=("base_price_in_cr", "count"),
    base_usd=("base_price_usd", "count"))
print(summary.to_string())