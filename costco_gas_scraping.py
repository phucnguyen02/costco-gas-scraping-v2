from bs4 import BeautifulSoup
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
HEADERS = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0' }

urls = ["https://www.costco.com/warehouse-locations/tustin-ranch-tustin-ca-122.html",
        "https://www.costco.com/warehouse-locations/garden-grove-ca-126.html",
        "https://www.costco.com/warehouse-locations/tustin-ca-1001.html",
        "https://www.costco.com/warehouse-locations/fullerton-ca-418.html",
        "https://www.costco.com/warehouse-locations/laguna-niguel-ca-28.html",
        "https://www.costco.com/warehouse-locations/laguna-marketplace-laguna-niguel-ca-690.html",
        "https://www.costco.com/warehouse-locations/huntington-beach-ca-1110.html",
        "https://www.costco.com/warehouse-locations/fountain-valley-ca-411.html",
        "https://www.costco.com/warehouse-locations/irvine-ca-454.html"]


db.collection('warehouses')


def scrape_gas(urls):
    f = open("output.txt", "w")
    for url in urls:
        r = requests.get(url, timeout = 5, headers = HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        prices = soup.find_all("span", {"class": "gas-type"})
        name = soup.find("div", {"class": "warehouse-name"}).find("h1").text
        address = soup.find("span", {"id": "address"}).find("span").text
        regular_gas = prices[0].parent.find_all("span")[1].text[:-1]
        premium_gas = prices[1].parent.find_all("span")[1].text[:-1]
        f.write("Name: " + name + ". Address: " + address + ". Regular Gas: " + regular_gas + ". Premium Gas: " + premium_gas + "\n")
        data = {'Name': name, 'Address': address, 'Regular_Gas': regular_gas, 'Premium_Gas': premium_gas}
        available = db.collection('warehouses').document(name).get()
        if available.exists:
            db.collection('warehouses').document(name).update(data)
        else:
            db.collection('warehouses').document(name).set(data)
    f.close()


scrape_gas(urls)