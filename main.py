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

#Credentials for Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

#Initializing the Firestore client
db = firestore.client()

#Headers for the request
HEADERS = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0' }

#Entry function for Google Cloud Functions
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

def scrape_gas():
    for url in warehouse_urls.urls:
        #A request is made to each gas station page, and times out within 5 seconds
        r = requests.get(url, timeout = 5, headers = HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        #Retrieves the gas prices and name of the gas station, along with its entry in the Firestore database
        gas_types = soup.find_all("span", {"class": "gas-type"})
        name = soup.find("div", {"class": "warehouse-name"}).find("h1").text
        cur_entry = db.collection('warehouses').document(name).get()

        #If this station does sell gas, then it continues scraping the types of gas
        if gas_types:
            address = soup.find("span", {"id": "address"}).find("span").text
            city = soup.find("span", {"id": "address"}).find_all("span")[1].text
            state = soup.find("span", {"id": "address"}).find_all("span")[2].text

            regular_gas = "?"
            premium_gas = "?"

            #If the station is only selling 1 gas type, the type is checked so the corresponding price is updated
            if len(gas_types) == 1:
                price = gas_types[0].parent.find_all("span")[1].text[:-1]
                if gas_types[0].parent.find("span").text == "Regular":
                    regular_gas = price
                else:
                    premium_gas = price

            #Otherwise, both prices are updated
            else:
                regular_gas = gas_types[0].parent.find_all("span")[1].text[:-1]
                premium_gas = gas_types[1].parent.find_all("span")[1].text[:-1]

            #Creates a new entry for the Firestore database
            data = {'Name': name, 'Address': address, 'City': city, 'State': state, 'Regular_Gas': regular_gas, 'Premium_Gas': premium_gas}

            #Current time based on Pacific Time
            cur_time = str(datetime.datetime.now(pytz.timezone("US/Pacific")))

            #If the entry for the station already exists within the Firestore database,
            #it checks if each type of gas has a different price from a previous scrape.
            #If this is true for either type, then the time would be updated to the current time
            #If the entry doesn't exist in the database yet, a new entry would be created with the updated
            #time being the current time.
            if cur_entry.exists:
                cur_regular = cur_entry.to_dict()['Regular_Gas']
                cur_premium = cur_entry.to_dict()['Premium_Gas']
                if cur_regular != regular_gas or cur_premium != premium_gas:   
                    data['Updated_Time'] = cur_time
                db.collection('warehouses').document(name).update(data)
            else:
                data['Updated_Time'] = cur_time
                db.collection('warehouses').document(name).set(data)
        
        #If the gas station isn't selling either type of gas, its corresponding entry is deleted from the database.
        else:
            if cur_entry.exists:
                db.collection('warehouses').document(name).delete()
                
scrape_gas()
