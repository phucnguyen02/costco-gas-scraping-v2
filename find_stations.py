from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome("chromedriver")
wait = WebDriverWait(driver, 3)
location = "LA"

driver.get("https://www.costco.com/warehouse-locations?langId=-1&storeId=10301&catalogId=10701")
time.sleep(3)

#Send location to website
input_box = driver.find_element("id", "search-warehouse")
input_box.click()
input_box.clear()
input_box.send_keys(location)
input_box.send_keys(Keys.ENTER)
time.sleep(3)

#Retrieve the URLs to all the stores within Irvine, CA
urls = set()
for link in driver.find_elements(By.TAG_NAME, "a"):
    string_link = link.get_attribute("href")
    if string_link and string_link.startswith("https://www.costco.com/warehouse-locations/"):
        urls.add(string_link)

driver.close()
