import firebase_admin
import pandas
from firebase_admin import credentials
from firebase_admin import firestore

#Credentials for Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

#Initializing the Firestore client
db = firestore.client()

def update_db(fuel_type, car_list):
    cur_entry = db.collection('car_brands').document(fuel_type).get()

    #Updates the database
    if not cur_entry.exists:
        db.collection('car_brands').document(fuel_type).set({fuel_type: car_list})
    else:
        db.collection('car_brands').document(fuel_type).update({fuel_type: car_list})

def check_csv():
    # Retrieve only the car make, model and fuel type
    csv_file = pandas.read_csv('vehicles.csv', header=0,usecols=['make', 'model', 'fuelType'])

    # Sets of cars that use regular or premium gas. We're using a set so that every car brand is unique
    regular_cars = set()
    premium_cars = set()
    for (index, car) in csv_file.iterrows():
        car_name = car['make'] + " " + car['model']
        if car['fuelType'] == 'Regular': regular_cars.add(car_name)
        else: premium_cars.add(car_name)

    update_db('Regular', regular_cars)
    update_db('Premium', premium_cars)

check_csv()



