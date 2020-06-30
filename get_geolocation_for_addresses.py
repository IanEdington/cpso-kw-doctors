import json
import os
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

import utils

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

GOOGLE_GEOCODE_API_BASE = "https://maps.googleapis.com/maps/api/geocode/json?"


def query_location_api(address):
    query = urlencode({"address": address, "key": GOOGLE_PLACES_API_KEY})
    response = requests.get(GOOGLE_GEOCODE_API_BASE + query)
    return response.text


def get_location(address):
    location_file = utils.get_location_data_file(address)
    if location_file.exists():
        location_data = location_file.read_text()
    else:
        location_file.parent.mkdir(parents=True, exist_ok=True)
        location_data = query_location_api(address)
        location_file.write_text(location_data)
    return json.loads(location_data)


def get_lat_lng_from_google_response(location_data):
    location = location_data["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]


def get_doctors_with_lat_long():
    # import csv into pandas
    doctors_df = pd.read_csv(utils.DOCTORS_OVERVIEW_CSV_FILE)

    # get lat, long for each
    doctor_locations = {}
    for index, doctor in doctors_df.iterrows():
        doctor_locations[doctor.cpso] = get_location(doctor.location)
        lat, lng = get_lat_lng_from_google_response(doctor_locations[doctor.cpso])

    doctors_df['lat'] = doctors_df['cpso'].apply(lambda cpso: get_lat_lng_from_google_response(doctor_locations[cpso])[0])
    doctors_df['lng'] = doctors_df['cpso'].apply(lambda cpso: get_lat_lng_from_google_response(doctor_locations[cpso])[1])

    return doctors_df

