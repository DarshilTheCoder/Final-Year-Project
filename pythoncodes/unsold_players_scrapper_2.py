"""
Scrape the 2025 / 2026 IPL AUCTION TABLE pages (Sold / Unsold / All Players tabs).


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

LINKS_FILE = "unsold_list.txt"     
OUT_DIR    = Path("data/unsold_and_sold_auction_pages")
CHROME_VER = 149

TABLE_SEL = "table.ds-table"                    
ROW_SEL   = "table.ds-table tbody tr"          



def slug_from(url):
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


            try:
                WebDriverWait(driver2, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_SEL))
                )
            except TimeoutException:
                print("   no table found - is this the right tab URL?")
                failed.append(link)
                continue

            stable = 0
            last_rows = 0
            for _ in range(40): 
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


            data = driver2.page_source
            out_path = OUT_DIR / f"{slug_from(link)}.html"
            with open(out_path, 'w', encoding='utf-8') as f:  
                f.write(data)


            n_rows  = len(driver2.find_elements(By.CSS_SELECTOR, ROW_SEL))
            n_links = len(driver2.find_elements(
                By.CSS_SELECTOR, "table.ds-table a[href*='/cricketers/']"))
            has_json = "__NEXT_DATA__" in data
            print(f"   saved {out_path.name} | {len(data):,} chars | "
                  f"rows: {n_rows} | player links: {n_links} | __NEXT_DATA__: {has_json}")
            if n_rows and n_links < n_rows:
                print(f"   note: {n_rows - n_links} row(s) have no player link")

            time.sleep(2)                 
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