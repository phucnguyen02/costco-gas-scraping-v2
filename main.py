from flask import escape

import functions_framework

from bs4 import BeautifulSoup
import requests
import datetime
import warehouse_urls
import pytz

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
HEADERS = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0' }

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "name" in request_json:
        name = request_json["name"]
    elif request_args and "name" in request_args:
        name = request_args["name"]
    else:
        name = "World"
    return f"Hello {escape(name)}!"

def scrape_gas(urls):
    for url in urls:
        r = requests.get(url, timeout = 5, headers = HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        prices = soup.find_all("span", {"class": "gas-type"})
        if prices:
            name = soup.find("div", {"class": "warehouse-name"}).find("h1").text
            address = soup.find("span", {"id": "address"}).find("span").text
            city = soup.find("span", {"id": "address"}).find_all("span")[1].text
            state = soup.find("span", {"id": "address"}).find_all("span")[2].text
            regular_gas = prices[0].parent.find_all("span")[1].text[:-1]
            premium_gas = prices[1].parent.find_all("span")[1].text[:-1]
            data = {'Name': name, 'Address': address, 'City': city, 'State': state, 'Regular_Gas': regular_gas, 'Premium_Gas': premium_gas}
            cur_entry = db.collection('warehouses').document(name).get()
            cur_time = str(datetime.datetime.now(pytz.timezone("US/Pacific")))
            if cur_entry.exists:
                cur_regular = cur_entry.to_dict()['Regular_Gas']
                cur_premium = cur_entry.to_dict()['Premium_Gas']
                if cur_regular != regular_gas or cur_premium != premium_gas:   
                    data['Updated_Time'] = cur_time
                db.collection('warehouses').document(name).update(data)
            else:
                data['Updated_Time'] = cur_time
                db.collection('warehouses').document(name).set(data)

                
scrape_gas(warehouse_urls.urls)
