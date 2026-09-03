"""This auction scrapper is used to scrap auction data of year 2011/12/13/15/16 and 25/26. 
2008 is scrapped using Kaggle, 2010 and 2009 I made it manually as no such proper data available"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os

os.makedirs('auction_data', exist_ok=True)

URL = "https://www.cricinfo.com/story/list-of-players-sold-and-unsold-at-ipl-auction-2016-969473"

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
        EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
    )
    time.sleep(3) 

    html = driver.page_source
    with open('auction_data/ipl-2016-auction.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved. Page source length:", len(html))

driver.quit()