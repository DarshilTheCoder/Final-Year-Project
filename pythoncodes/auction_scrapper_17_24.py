"""This auction_scrapper is used to scrap auction data of 2014/17/18/19/20/21/22/23/24"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os

os.makedirs('auction_data', exist_ok=True)
URL = "https://www.espncricinfo.com/ipl2014_auction/content/site/ipl2014_auction/index.html"

driver = uc.Chrome(version_main=149)
driver.get(URL)

try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    ).click()
except:
    pass

if "Access Denied" in driver.page_source:
    print("STILL BLOCKED")
else:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table table-hover mb-0"))
    )
    time.sleep(3)

    html = driver.page_source
    year = 2014
    with open(f'auction_data/ipl-{year}-auction.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved. Length:", len(html))

    # # quick self-check: how many team blocks made it into the saved HTML?
    # from bs4 import BeautifulSoup
    # soup = BeautifulSoup(html, 'html.parser')
    # teams = soup.select("div[id^='team_']")
    # print(f"Team blocks captured: {len(teams)}")   # want 10

driver.quit()