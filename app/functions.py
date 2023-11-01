import os
import random

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
API_KEY = os.getenv("TMAP_APP_KEY")


def make_auth_code():
    # return "".join([str(random.randint(0, 9)) for _ in range(6)])
    return str(random.randint(1, 9)) + "".join([str(random.randint(0, 9)) for _ in range(5)])


def send_sms(phone, text):
    if phone[0] != "+":
        phone = "+82" + phone[1:]

    client = boto3.client(
        "sns",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1",
    )

    client.publish(
        PhoneNumber=phone,
        Message=text,
    )

    print(f"Sent SMS to {phone} with text: {text}")


def poi_search(search_query: str):
    query = {
        "version": "1",
        "searchKeyword": search_query,
    }

    # urlparam = "&".join([f"{k}={v}" for k, v in query.items()])
    # poi_api_url = f"https://apis.openapi.sk.com/tmap/pois?{urlparam}"

    headers = {
        "appKey": API_KEY,
        "Accept": "application/json"
    }

    response = requests.get("https://apis.openapi.sk.com/tmap/pois", headers=headers, params=query)
    return response.json()


def route_search(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    body = {
        "startX": start_lon,
        "startY": start_lat,
        "endX": end_lon,
        "endY": end_lat,
        "count": 1,
        "lang": 0,
        "format": "json"
    }

    headers = {
        "accept": "application/json",
        "appKey": API_KEY,
        "content-type": "application/json"
    }

    response = requests.post("https://apis.openapi.sk.com/transit/routes", headers=headers, json=body)
    return response.json()


def get_location(poi_id: int):
    # https://apis.openapi.sk.com/tmap/pois/{poiInfo}?version={version}&resCoordType={resCoordType}&callback={callback}&appKey={appKey}
    query = {
        "version": "1",
        "resCoordType": "WGS84GEO",
    }
    headers = {
        "accept": "application/json",
        "appKey": API_KEY,
    }

    response = requests.get(f"https://apis.openapi.sk.com/tmap/pois/{poi_id}", headers=headers, params=query)
    return response.json()


def reverse_geocoding(lat: float, lon: float):
    query = {
        "version": "1",
        "format": "json",
        "callback": "result",
        "coordType": "WGS84GEO",
        "addressType": "A10",
        "lon": lon,
        "lat": lat
    }

    headers = {
        # "accept": "application/json",
        "appKey": API_KEY,
    }

    response = requests.get("https://apis.openapi.sk.com/tmap/geo/reversegeocoding", headers=headers, params=query)
    return {"poi": poi_search(response.json()["addressInfo"]["fullAddress"])["searchPoiInfo"]["pois"]["poi"][0]["id"]}
