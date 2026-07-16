import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os

os.makedirs('auction_data', exist_ok=True)

URL = "https://www.cricinfo.com/story/list-of-players-sold-and-unsold-at-ipl-auction-2016-969473"

driver = uc.Chrome(version_main=149)
driver.get(URL)

# dismiss cookie banner if it appears
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
    time.sleep(3)   # let the tables render

    html = driver.page_source
    with open('auction_data/ipl-2016-auction.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved. Page source length:", len(html))

driver.quit()