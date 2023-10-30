from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import functions
import redis
from uuid import UUID
from sqlmodel import SQLModel, create_engine, Session
import schemas
from functions import UserJWT, decode_jwt
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

origin = [
    "http://localhost:5173",
    "https://dev.ride.moda",
    "https://ride.moda"
]

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
        user = session.query(schemas.User).filter(schemas.User.phone_number == phone_number).first()
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
        user = session.query(schemas.User).filter(schemas.User.phone_number == phone_number).first()
        if user is None:
            raise HTTPException(status_code=400, detail="가입이 필요해요.")

    if redis_client.get(f"auth_code:{phone_number}") == auth_code:
        with Session(engine) as session:
            user = session.query(schemas.User).filter(schemas.User.phone_number == phone_number).first()
            if user is None:
                raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
            else:
                return {"message": "Success", "token": functions.generate_jwt(UserJWT(phone_number=user.phone_number,
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
        user = session.query(schemas.User).filter(schemas.User.phone_number == phone_number).first()
        if user is not None:
            raise HTTPException(status_code=400, detail="이미 가입된 번호에요.")

        user = schemas.User(phone_number=phone_number, username=username, card_number=card_number)
        session.add(user)
        session.commit()
        session.refresh(user)

    return {"message": "Success", "user": user}


@app.post("/user/get_user", tags=["user"])
def get_user(phone: Phone):
    phone_number = "".join([c for c in phone.phone_number if c.isnumeric()])
    with Session(engine) as session:
        user = session.query(schemas.User).filter(schemas.User.phone_number == phone_number).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            return {"message": "Success", "user": user}


class UserUpdate(BaseModel):
    username: str
    card_number: str


@app.put("/user/update_user", tags=["user"])
def update_user(user: UserUpdate, token: Annotated[UserJWT, decode_jwt]):
    username = user.username
    card_number = user.card_number

    with Session(engine) as session:
        user = session.query(schemas.User).filter(schemas.User.phone_number == token.phone_number).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            user.username = username
            user.card_number = card_number
            session.commit()
            session.refresh(user)
            # get new jwt
            return {"message": "Success", "token": functions.generate_jwt(UserJWT(phone_number=user.phone_number,
                                                                                  username=user.username,
                                                                                  card_number=user.card_number))}


class PhoneUpdate(BaseModel):
    phone_number: str
    auth_code: str


@app.put("/user/update_phone", tags=["user"])
def update_phone(phone: PhoneUpdate, token: Annotated[UserJWT, decode_jwt]):
    phone_number = "".join([c for c in phone.phone_number if c.isnumeric()])
    auth_code = phone.auth_code

    if redis_client.get(f"auth_code:{phone_number}") != auth_code:
        raise HTTPException(status_code=400, detail="인증번호가 일치하지 않아요.")

    with Session(engine) as session:
        user = session.query(schemas.User).filter(schemas.User.phone_number == token.phone_number).first()
        if user is None:
            raise HTTPException(status_code=400, detail="존재하지 않는 유저에요.")
        else:
            user.phone_number = phone_number
            session.commit()
            session.refresh(user)
            # get new jwt
            return {"message": "Success", "token": functions.generate_jwt(UserJWT(phone_number=user.phone_number,
                                                                                  username=user.username,
                                                                                  card_number=user.card_number))}


@app.delete("/user/delete_user", tags=["user"])
def delete_user(token: Annotated[UserJWT, decode_jwt]):
    with Session(engine) as session:
        user = session.query(schemas.User).filter(schemas.User.phone_number == token.phone_number).first()
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
