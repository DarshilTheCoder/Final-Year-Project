from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import undetected_chromedriver as uc


driver2 = uc.Chrome(version_main=149)
with open('data/players_list.txt','r') as file:
    for line_number, line in enumerate(file, start=1):
        print(line_number, line.strip())
        link = line.rstrip('\n')
        slug = link.split('/')[-1]
        print(slug)
        driver2.get(link)
        try:
            WebDriverWait(driver2, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
        except:
            pass
        if "Access Denied" in driver2.page_source:
            print('You are Blocked')
        else:
            WebDriverWait(driver2, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "i.icon-expand_more-filled"))
            )
            arrows = driver2.find_elements(By.CSS_SELECTOR, "i.icon-expand_more-filled")
            print(arrows)
            for a in arrows:
                driver2.execute_script("arguments[0].click();", a)
                time.sleep(1)
            data = driver2.page_source
            with open(f'data/{slug}.html','a',encoding='utf-8') as f:
                f.write(data)
    print(line_number)
try:
    driver2.quit()
except Exception:
    pass