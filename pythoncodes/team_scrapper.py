"""team_scrapper is the file which is used to scrap the each team players link from the ESPN website. 
"""


import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = uc.Chrome(version_main=149)
driver.get("https://www.espncricinfo.com/records/trophy/averages-batting/indian-premier-league-117?team=6904")

if "Access Denied" in driver.page_source:
    print("STILL BLOCKED")
else:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ds-min-w-max"))
    )
    elems = driver.find_elements(By.CSS_SELECTOR,"td a[href*='/cricketers/']")

    with open('data/players_list.txt','a',encoding='utf-8') as f:
        for elem in elems:
            data = elem.get_attribute('href')
            f.write(data+"\n")
driver.quit()