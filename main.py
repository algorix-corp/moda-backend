from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import functions
import redis
from uuid import UUID
from sqlmodel import SQLModel, create_engine, Session
import schemas

app = FastAPI(title="MODA API")
load_dotenv()

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
    auth_code = functions.make_auth_code()
    redis_client.set(f"auth_code:{phone_number}", auth_code, ex=300)
    functions.send_sms(phone_number, f"The MODA Authentication Code is {auth_code}")
    return {"message": "Sent auth code"}


class VerifyPhone(BaseModel):
    phone_number: str
    auth_code: str


@app.post("/auth/verify_phone", tags=["auth"])
def verify_phone(verify_phone: VerifyPhone):
    phone_number = "".join([c for c in verify_phone.phone_number if c.isnumeric()])
    auth_code = verify_phone.auth_code
    if redis_client.get(f"auth_code:{phone_number}") == auth_code:
        return {"message": "Success"}
    else:
        return {"message": "Fail"}


class CreateUser(BaseModel):
    phone_number: str
    username: str
    card_number: str


@app.post("/user/create_user", tags=["user"])
def create_user(create_user: CreateUser):
    phone_number = "".join([c for c in create_user.phone_number if c.isnumeric()])
    username = create_user.username
    card_number = create_user.card_number

    with Session(engine) as session:
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
            return {"message": "Fail", "user": None}
        else:
            return {"message": "Success", "user": user}


class UserUpdate(BaseModel):
    user_id: UUID
    phone_number: str
    username: str
    card_number: str


@app.put("/user/update_user", tags=["user"])
def update_user(user: UserUpdate):
    user_id = user.user_id
    phone_number = "".join([c for c in user.phone_number if c.isnumeric()])
    username = user.username
    card_number = user.card_number

    with Session(engine) as session:
        user = session.query(schemas.User).filter(schemas.User.id == user_id).first()
        if user is None:
            return {"message": "Fail", "user": None}
        else:
            user.phone_number = phone_number
            user.username = username
            user.card_number = card_number
            session.commit()
            session.refresh(user)
            return {"message": "Success", "user": user}


@app.delete("/user/delete_user?user_id", tags=["user"])
def delete_user(user_id: UUID):
    with Session(engine) as session:
        user = session.query(schemas.User).filter(schemas.User.id == user_id).first()
        if user is None:
            return {"message": "Fail", "user": None}
        else:
            session.delete(user)
            session.commit()
            return {"message": "Success"}
