import requests
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlmodel import create_engine

from dependencies import get_token_data, issue_token
from schema import *

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
TRANSIT_API_URL = "https://apis.openapi.sk.com/transit/routes"
POI_API_URL = "https://apis.openapi.sk.com/tmap/pois"
API_KEY = "fbvcs7KASx8FIk74NL6pSUI7M9VbxXz7HOIaDpL4"


@app.on_event("startup")
def on_startup():
    global engine
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)


@app.post("/poi_search")
def poi_search(search_keyword: str):
    query = {
        "version": "1",
        "searchKeyword": search_keyword,
    }

    urlparam = "&".join([f"{k}={v}" for k, v in query.items()])
    poi_api_url = f"{POI_API_URL}?{urlparam}"

    headers = {
        "appKey": API_KEY,
        "Accept": "application/json"
    }

    response = requests.get(poi_api_url, headers=headers)
    return response.json()


@app.post("/route_search")
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

    response = requests.post(TRANSIT_API_URL, headers=headers, json=body)
    return response.json()


class User(BaseModel):
    phone: str
    name: str


@app.post("/auth")
def auth(user: User):
    return issue_token(user.dict())
#
#
#
#
# @app.post("/reserve_drt")
# def reserve_drt(data: dict = Depends(get_token_data)):
#     return data

