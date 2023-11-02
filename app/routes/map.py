from fastapi import APIRouter

from app.functions import poi_search, route_search, get_location, reverse_geocoding

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


@router.get("/reverse_geocoding")
def reverse_geocoding_api(lat: float, lon: float):
    return reverse_geocoding(lat, lon)


@router.get("/route")
def route(start_poi: str, end_poi: str):
    start_loc = get_location(start_poi)
    end_loc = get_location(end_poi)

    start_lat = float(start_loc["poiDetailInfo"]["lat"])
    start_lon = float(start_loc["poiDetailInfo"]["lon"])

    end_lat = float(end_loc["poiDetailInfo"]["lat"])
    end_lon = float(end_loc["poiDetailInfo"]["lon"])

    return route_search(start_lat, start_lon, end_lat, end_lon)


@router.get("/route_drt")
def route_drt(start_poi: str, end_poi: str):
    start_loc = get_location(start_poi)
    end_loc = get_location(end_poi)

    start_lat = float(start_loc["poiDetailInfo"]["lat"])
    start_lon = float(start_loc["poiDetailInfo"]["lon"])

    end_lat = float(end_loc["poiDetailInfo"]["lat"])
    end_lon = float(end_loc["poiDetailInfo"]["lon"])

    route = route_search(start_lat, start_lon, end_lat, end_lon)
    print(route)

    try:
        fareWon = route["metaData"]["plan"]["itineraries"][0]["fare"]["regular"]["totalFare"]
        timeMinute = route["metaData"]["plan"]["itineraries"][0]["totalTime"]

        return {
            "route": route["metaData"]["plan"]["itineraries"][0]["legs"],
            "fareWon": fareWon + 1500,
            "timeMinute": timeMinute / 60,
            "savedWon": "3500",
            "savedMinute": "20"
        }
    except KeyError:
        return {
            "route": route["metaData"]["plan"]["itineraries"][0]["legs"],
            "fareWon": -1,
            "timeMinute": -1,
            "savedWon": -1,
            "savedMinute": -1
        }

# resp = route_drt("1866614", "535438")
# print(resp)
