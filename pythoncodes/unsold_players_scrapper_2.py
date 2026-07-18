"""
Scrape the 2025 / 2026 IPL AUCTION TABLE pages (Sold / Unsold / All Players tabs).

These are not story pages - the players sit in a real <table class="ds-table">
that renders with React, so:
  - we wait for the table, not for div.Article / article.ci-story
  - we scroll until the ROW COUNT stops growing (a table can keep loading rows
    long after the page height settles)
  - after saving we report the row count and whether __NEXT_DATA__ is present,
    because if the JSON payload is in the page you should parse THAT instead of
    walking <td> cells.

Saves the full page_source, same as the other scrapers. Parsing comes later.
https://www.cricinfo.com/auction/ipl-2026-auction-1515016/unsold-players
https://www.cricinfo.com/auction/ipl-2025-auction-1460972/unsold-players

it is used for 2025/2026
"""

import re
import time
from pathlib import Path

import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---- EDIT THESE ----------------------------------------------------------
LINKS_FILE = "unsold_list.txt"      # one URL per line, next to this script
OUT_DIR    = Path("data/unsold_and_sold_auction_pages")
CHROME_VER = 149

TABLE_SEL = "table.ds-table"                    # the players table
ROW_SEL   = "table.ds-table tbody tr"           # one row per player
# --------------------------------------------------------------------------


def slug_from(url):
    """Last TWO path segments -> unique filename.
    .../ipl-2026-auction-1521234/unsold-players -> ipl-2026-auction-1521234_unsold-players

    The last segment alone is NOT enough here: the 2025 and 2026 pages both end
    in 'unsold-players', so one would silently overwrite the other.
    """
    path = url.split("?")[0].split("#")[0].rstrip("/")
    parts = [p for p in path.split("/") if p][-2:]
    return re.sub(r"[^A-Za-z0-9._-]", "_", "_".join(parts)) or "page"


OUT_DIR.mkdir(parents=True, exist_ok=True)
driver2 = uc.Chrome(version_main=CHROME_VER)
failed = []

try:
    with open(LINKS_FILE, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            link = line.strip()
            if not link:
                continue

            print(f"{line_number} {link}")
            driver2.get(link)

            # cookie banner (not always shown)
            try:
                WebDriverWait(driver2, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                ).click()
            except TimeoutException:
                pass

            if "Access Denied" in driver2.page_source:
                print("   You are Blocked")
                failed.append(link)
                continue

            # wait for the players TABLE to render
            try:
                WebDriverWait(driver2, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_SEL))
                )
            except TimeoutException:
                print("   no table found - is this the right tab URL?")
                failed.append(link)
                continue

            # Scroll until the ROW COUNT stops growing. Height alone is not a
            # reliable signal for a lazy-loading table, so we count rows and
            # stop only after 3 scrolls with no new ones.
            stable = 0
            last_rows = 0
            for _ in range(40): #why 40 only and not anyother value??
                rows_now = len(driver2.find_elements(By.CSS_SELECTOR, ROW_SEL))
                if rows_now == last_rows:
                    stable += 1
                    if stable >= 3:
                        break
                else:
                    stable = 0
                last_rows = rows_now
                driver2.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                time.sleep(1)

            # SAVE THE WHOLE PAGE - same as the other scrapers.
            data = driver2.page_source
            out_path = OUT_DIR / f"{slug_from(link)}.html"
            with open(out_path, 'w', encoding='utf-8') as f:   # 'w' not 'a'
                f.write(data)

            # verify-as-you-go
            n_rows  = len(driver2.find_elements(By.CSS_SELECTOR, ROW_SEL))
            n_links = len(driver2.find_elements(
                By.CSS_SELECTOR, "table.ds-table a[href*='/cricketers/']"))
            has_json = "__NEXT_DATA__" in data
            print(f"   saved {out_path.name} | {len(data):,} chars | "
                  f"rows: {n_rows} | player links: {n_links} | __NEXT_DATA__: {has_json}")
            if n_rows and n_links < n_rows:
                print(f"   note: {n_rows - n_links} row(s) have no player link")

            time.sleep(2)                       # be polite between pages
finally:
    try:
        driver2.quit()
    except Exception:
        pass

if failed:
    print(f"\n{len(failed)} pages failed:")
    for l in failed:
        print("  ", l)
else:
    print("\nAll pages saved.")