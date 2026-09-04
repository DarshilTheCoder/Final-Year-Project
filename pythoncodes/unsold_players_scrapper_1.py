"""
Scrape ESPNcricinfo AUCTION STORY pages (the sold + unsold player lists).

  to scrap 2015/2017/2018/2019/2020/2021/2024 (coming from unsold_list_0.txt)
  https://www.cricinfo.com/story/list-of-players-sold-and-unsold-in-ipl-2015-auction-832783?platform=amp
https://www.cricinfo.com/story/list-of-players-sold-and-unsold-at-ipl-auction-2017-1083407?platform=amp
https://www.cricinfo.com/story/ipl-2018-player-auction-list-of-sold-and-unsold-players-1134446?platform=amp
https://www.cricinfo.com/story/ipl-2019-auction-the-list-of-sold-and-unsold-players-1166896?platform=amp
https://www.cricinfo.com/story/ipl-2020-auction-the-list-of-sold-and-unsold-players-1210538?platform=amp
https://www.cricinfo.com/story/ipl-2021-auction-the-list-of-sold-and-unsold-players-1252152?platform=amp
https://www.cricinfo.com/story/ipl-2024-auction-the-list-of-sold-and-unsold-players-1413396?platform=amp


to scrap 2012/2013/2016/2022/2023 used unsold_list_1.txt
https://www.cricinfo.com/story/ipl-2012-auction-who-was-sold-to-whom-552053
https://www.cricinfo.com/story/ipl-player-list-at-2013-auction-603194
https://www.cricinfo.com/story/list-of-players-sold-and-unsold-at-ipl-auction-2016-969473
https://www.cricinfo.com/story/ipl-2022-auction-the-list-of-sold-and-unsold-players-1300689
https://www.cricinfo.com/story/2023-ipl-auction-list-of-sold-unsold-players-1350272

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


def slug_from(url):
    slug = url.split("?")[0].split("#")[0].rstrip("/").split("/")[-1]
    return re.sub(r"[^A-Za-z0-9._-]", "_", slug) or "page"


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
                WebDriverWait(driver2, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Article,article.ci-story h2"))
                )
            except TimeoutException:
                print("   no div.Article - different layout?")
                failed.append(link)
                continue


            last_height = 0
            for _ in range(20):
                driver2.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                height = driver2.execute_script("return document.body.scrollHeight")
                if height == last_height:
                    break
                last_height = height

            data = driver2.page_source
            out_path = OUT_DIR / f"{slug_from(link)}.html"
            with open(out_path, 'w', encoding='utf-8') as f:   
                f.write(data)

            heads = [h.text.strip() for h in
                     driver2.find_elements(By.CSS_SELECTOR, "div.Article h2,article.ci-story h2")
                     if h.text.strip()]
            print(f"   saved {out_path.name} | {len(data):,} chars | sections: {heads[:6]}")

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