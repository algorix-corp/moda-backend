from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import functions
import redis
from uuid import UUID
from sqlmodel import SQLModel, create_engine, Session, select
import schemas
from functions import UserJWT, decode_jwt
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

origin = [
    "http://localhost:5173",
    "https://dev.ride.moda",
    "https://ride.moda"
]

engine = None

app = FastAPI(title="MODA API")
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)


@app.on_event("startup")
def startup():
    print("===== Startup =====")
    print(f"REDIS: {redis_client.info('server')['redis_version']}")

    POSTGRES_DATABASE_URL = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}")

    global engine
    engine = create_engine(POSTGRES_DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    print("SQLModel metadata created")

    print("===================")


@app.on_event("shutdown")
def shutdown():
    print("===== Shutdown =====")
    print("Bye!")
    redis_client.close()
    print("====================")


@app.get("/", name="Hello, World!")
def hello_world():
    return {"message": f"Hello, World! From {os.getenv('ENDPOINT_URL')}"}


class Phone(BaseModel):
    phone_number: str


@app.post("/auth/send_auth_code", tags=["auth"])
def phone_(phone: Phone):
    phone_number = "".join([c for c in phone.phone_number if c.isnumeric()])
    new_user = False

    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.phone_number == phone_number)
        user = session.exec(query).first()
        if user is None:
            new_user = True

    auth_code = functions.make_auth_code()
    redis_client.set(f"auth_code:{phone_number}", auth_code, ex=300)
    functions.send_sms(phone_number, f"[MODA]\n인증번호: {auth_code}")
    return {"message": "Sent auth code", "register": new_user}


class VerifyPhone(BaseModel):
    phone_number: str
    auth_code: str


@app.post("/auth/verify_phone", tags=["auth"])
def verify_phone(verify_data: VerifyPhone):
    phone_number = "".join([c for c in verify_data.phone_number if c.isnumeric()])
    auth_code = verify_data.auth_code

    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.phone_number == phone_number)
        user = session.exec(query).first()
        if user is None:
            raise HTTPException(status_code=400, detail="가입이 필요해요.")

    if redis_client.get(f"auth_code:{phone_number}") == auth_code:
        return {"message": "Success", "token": functions.generate_jwt(UserJWT(id=user.id,
                                                                              phone_number=user.phone_number,
                                                                              username=user.username,
                                                                              card_number=user.card_number))}
    else:
        raise HTTPException(status_code=400, detail="인증번호가 일치하지 않아요.")


class CreateUser(BaseModel):
    phone_number: str
    username: str
    card_number: str
    auth_code: str


@app.post("/user/create_user", tags=["user"])
def create_user(create_data: CreateUser):
    phone_number = "".join([c for c in create_data.phone_number if c.isnumeric()])
    username = create_data.username
    card_number = create_data.card_number
    auth_code = create_data.auth_code

    if redis_client.get(f"auth_code:{phone_number}") != auth_code:
        raise HTTPException(status_code=400, detail="인증번호가 일치하지 않아요.")

    with Session(engine) as session:
        # check if user already exists
        query = select(schemas.User).where(schemas.User.phone_number == phone_number)
        user = session.exec(query).first()
        if user is not None:
            raise HTTPException(status_code=400, detail="이미 가입된 번호에요.")

        user = schemas.User(phone_number=phone_number, username=username, card_number=card_number)
        session.add(user)
        session.commit()
        session.refresh(user)

    return {"message": "Success", "user": user}


@app.post("/user/get_user", tags=["user"])
def get_user(token: Annotated[UserJWT, Depends(decode_jwt)]):
    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.id == token.id)
        user = session.exec(query).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            return {"message": "Success", "user": user}


class UserUpdate(BaseModel):
    username: str
    card_number: str


@app.put("/user/update_user", tags=["user"])
def update_user(user: UserUpdate, token: Annotated[UserJWT, Depends(decode_jwt)]):
    username = user.username
    card_number = user.card_number

    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.id == token.id)
        user = session.exec(query).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            user.username = username
            user.card_number = card_number
            session.commit()
            session.refresh(user)
            # get new jwt
            return {"message": "Success", "token": functions.generate_jwt(UserJWT(id=user.id,
                                                                                  phone_number=user.phone_number,
                                                                                  username=user.username,
                                                                                  card_number=user.card_number))}


class PhoneUpdate(BaseModel):
    phone_number: str
    auth_code: str


@app.put("/user/update_phone", tags=["user"])
def update_phone(phone: PhoneUpdate, token: Annotated[UserJWT, Depends(decode_jwt)]):
    phone_number = "".join([c for c in phone.phone_number if c.isnumeric()])
    auth_code = phone.auth_code

    if redis_client.get(f"auth_code:{phone_number}") != auth_code:
        raise HTTPException(status_code=400, detail="인증번호가 일치하지 않아요.")

    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.phone_number == phone.phone_number)
        user = session.exec(query).first()
        if user is not None:
            raise HTTPException(status_code=400, detail="이미 가입된 번호에요.")

        query = select(schemas.User).where(schemas.User.id == token.id)
        user = session.exec(query).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            user.phone_number = phone_number
            session.commit()
            session.refresh(user)
            # get new jwt
            return {"message": "Success", "token": functions.generate_jwt(UserJWT(id=user.id,
                                                                                  phone_number=user.phone_number,
                                                                                  username=user.username,
                                                                                  card_number=user.card_number))}


@app.delete("/user/delete_user", tags=["user"])
def delete_user(token: Annotated[UserJWT, Depends(decode_jwt)]):
    with Session(engine) as session:
        query = select(schemas.User).where(schemas.User.id == token.id)
        user = session.exec(query).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            session.delete(user)
            session.commit()
            return {"message": "계정 삭제를 완료했어요."}


@app.get("/poi_search", tags=["poi"])
def poi_search(search_keyword: str):
    return functions.poi_search(search_keyword)


class RouteSearch(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


@app.post("/route_search", tags=["route"])
def route_search(data: RouteSearch):
    return functions.route_search(data.start_lat, data.start_lon, data.end_lat, data.end_lon)


class AddBookmark(BaseModel):
    location_name: str
    location_poi: int


@app.post("/bookmark/add_bookmark", tags=["bookmark"])
def add_bookmark(data: AddBookmark, token: Annotated[UserJWT, Depends(decode_jwt)]):
    location_name = data.location_name
    location_poi = data.location_poi
    with Session(engine) as session:
        bookmark = schemas.LocationBookmark(user_id=token.id, location_name=location_name, location_poi=location_poi)
        session.add(bookmark)
        session.commit()
        session.refresh(bookmark)
        return {"message": "Success", "bookmark": bookmark}


@app.get("/bookmark/get_bookmark", tags=["bookmark"])
def get_bookmark(token: Annotated[UserJWT, Depends(decode_jwt)]):
    with Session(engine) as session:
        query = select(schemas.LocationBookmark).where(schemas.LocationBookmark.user_id == token.id)
        bookmarks = session.exec(query).all()
        return {"message": "Success", "bookmarks": bookmarks}


class DeleteBookmark(BaseModel):
    bookmark_id: UUID


@app.delete("/bookmark/delete_bookmark", tags=["bookmark"])
def delete_bookmark(data: DeleteBookmark, token: Annotated[UserJWT, Depends(decode_jwt)]):
    bookmark_id = data.bookmark_id
    with Session(engine) as session:
        bookmark = session.query(schemas.LocationBookmark).filter(schemas.LocationBookmark.id == bookmark_id).first()
        if bookmark is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 북마크에요.")
        if bookmark.user_id != token.id:
            raise HTTPException(status_code=400, detail="삭제 권한이 없어요.")
        else:
            session.delete(bookmark)
            session.commit()
            return {"message": "북마크 삭제를 완료했어요."}


@app.get("/location")
def get_location(poi_id: int):
    return functions.get_location(poi_id)


class ReservationData(BaseModel):
    date: str
    time: str
    start_poi: int
    end_poi: int
    bus_id: UUID
    route: str
    estimated_time: str
    saved_time: str
    estimate_fee: int


@app.post("/reservation", tags=["drt"])
def make_reservation(data: ReservationData, token: Annotated[UserJWT, Depends(decode_jwt)]):
    date = data.date
    time = data.time
    start_poi = data.start_poi
    end_poi = data.end_poi
    bus_id = data.bus_id
    estimated_time = data.estimated_time
    saved_time = data.saved_time
    estimate_fee = data.estimate_fee

    with Session(engine) as session:
        new_res = schemas.DRTReservation(user_id=token.id, date=date, time=time, start_poi=start_poi,
                                         end_poi=end_poi, bus_id=bus_id,
                                         estimated_time=estimated_time, saved_time=saved_time,
                                         estimate_fee=estimate_fee)
        session.add(new_res)
        session.commit()
        session.refresh(new_res)
        return {"message": "Success", "reservation": new_res}


@app.get("/reservations", tags=["drt"])
def get_reservations(token: Annotated[UserJWT, Depends(decode_jwt)]):
    with Session(engine) as session:
        query = select(schemas.DRTReservation).where(schemas.DRTReservation.user_id == token.id)
        reservations = session.exec(query).all()
        return {"message": "Success", "reservations": reservations}


@app.get("/reservation/{reservation_id}", tags=["drt"])
def get_reservation_id(reservation_id: UUID, token: Annotated[UserJWT, Depends(decode_jwt)]):
    with Session(engine) as session:
        query = select(schemas.DRTReservation).where(schemas.DRTReservation.id == reservation_id)
        reservation = session.exec(query).first()
        if reservation is None:
            raise HTTPException(status_code=400, detail="예약이 존재하지 않아요.")
        if reservation.user_id != token.id:
            raise HTTPException(status_code=400, detail="조회 권한이 없어요.")
        else:
            return {"message": "Success", "reservation": reservation}


@app.delete("/reservation/{reservation_id}", tags=["drt"])
def delete_reservation_id(reservation_id: UUID, token: Annotated[UserJWT, Depends(decode_jwt)]):
    with Session(engine) as session:
        query = select(schemas.DRTReservation).where(schemas.DRTReservation.id == reservation_id)
        reservation = session.exec(query).first()
        if reservation is None:
            raise HTTPException(status_code=400, detail="예약이 존재하지 않아요.")
        if reservation.user_id != token.id:
            raise HTTPException(status_code=400, detail="삭제 권한이 없어요.")
        else:
            session.delete(reservation)
            session.commit()
            return {"message": "예약을 삭제했어요."}
