from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome("chromedriver")
wait = WebDriverWait(driver, 10)
location = "Irvine, CA"

driver.get("https://www.costco.com/warehouse-locations?langId=-1&storeId=10301&catalogId=10701")
#wait.until(EC.visibility_of_element_located((By.ID, "search-warehouse")))
time.sleep(3)

#Send location to website
input_box = driver.find_element("id", "search-warehouse")
input_box.click()
input_box.clear()
input_box.send_keys(location)
input_box.send_keys(Keys.ENTER)
#wait.until(EC.visibility_of_element_located((By.ID, "warehouse-list")))
time.sleep(3)

#Retrieve the URLs to all the stores within Irvine, CA
urls = set()
for link in driver.find_elements(By.TAG_NAME, "a"):
    string_link = link.get_attribute("href")
    if string_link and string_link.startswith("https://www.costco.com/warehouse-locations/"):
        urls.add(string_link)

#Visit all the URLs
f = open("output.txt", "w")
for url in urls:
    driver.get(url)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "warehouse-body")))

    #Check to see if the store has a gas station
    if driver.find_elements("xpath", '/html/body/main/div[3]/div[3]/div[3]/div[2]/div/div/div[2]/div[2]/div/div[5]/div[1]/span[2]'):
        warehouse_name = driver.find_element("xpath", '//*[@id="warehouse"]/div[3]/div[2]/h1').text
        warehouse_address = driver.find_element("xpath", '//*[@id="address"]/div[1]/span[1]').text
        regular_gas = driver.find_element("xpath", '/html/body/main/div[3]/div[3]/div[3]/div[2]/div/div/div[2]/div[2]/div/div[5]/div[1]/span[2]').get_attribute('innerHTML').split('<')[0]
        premium_gas = driver.find_element("xpath", '/html/body/main/div[3]/div[3]/div[3]/div[2]/div/div/div[2]/div[2]/div/div[5]/div[2]/span[2]').get_attribute('innerHTML').split('<')[0]
        f.write("Name: " + warehouse_name + ". Address: " + warehouse_address + ". Regular Gas: " + regular_gas + ". Premium Gas: " + premium_gas + "\n")
time.sleep(5)
f.close()
driver.close()