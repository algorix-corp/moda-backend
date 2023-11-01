from fastapi import APIRouter

from app.functions import poi_search, route_search, get_location

router = APIRouter(
    prefix="/map",
    tags=["Map"],
)


@router.get("/search/{keyword}")
def search(keyword: str):
    return poi_search(keyword)


@router.get("/poi/{poi_id}")
def get_poi(poi_id: str):
    return get_location(poi_id)


@router.get("/route")
def route(start_poi: str, end_poi: str):
    start_loc = get_location(start_poi)
    end_loc = get_location(end_poi)

    start_lat = float(start_loc["poiDetailInfo"]["lat"])
    start_lon = float(start_loc["poiDetailInfo"]["lon"])

    end_lat = float(end_loc["poiDetailInfo"]["lat"])
    end_lon = float(end_loc["poiDetailInfo"]["lon"])

    return route_search(start_lat, start_lon, end_lat, end_lon)
