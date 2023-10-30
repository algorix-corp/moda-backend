import boto3
import requests
from dotenv import load_dotenv
import os
import random
import jwt
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from uuid import UUID

import schemas

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
API_KEY = os.getenv("API_KEY")


# API_KEY = "fbvcs7KASx8FIk74NL6pSUI7M9VbxXz7HOIaDpL4"


class UserJWT(BaseModel):
    id: UUID
    phone_number: str
    username: str
    card_number: str


def generate_jwt(payload: UserJWT):
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str, engine) -> UserJWT:
    try:
        data = UserJWT(**jwt.decode(token, JWT_SECRET, algorithms=["HS256"]))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="인증하는데 문제가 발생했어요..")
    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.phone_number == data.phone_number)
        user = session.exec(query).first()
        if user is None:
            raise HTTPException(status_code=400, detail="인증하는데 문제가 발생했어요.")
    return data


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


def make_auth_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])


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
