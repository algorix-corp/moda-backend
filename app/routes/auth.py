from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.database import redis
from app.functions import send_sms, make_auth_code
from app.schemas import User

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class Phone(BaseModel):
    number: str


@router.post("/is_user_exist")
def is_user_exist(phone: Phone):
    phone_number = "".join(filter(str.isdigit, phone.number))
    with Session(engine) as session:
        statement = select(User).where(User.phone_number == phone_number)
        result = session.exec(statement)
        data = result.first()
        if data:
            return {"message": "exist", "user_id": data.id}
        else:
            return {"message": "not exist"}


@router.post("/send_code")
def send_code(phone: Phone):
    phone_number = "".join(filter(str.isdigit, phone.number))
    auth_code = make_auth_code()
    redis.set(phone_number, auth_code, ex=300)
    send_sms(phone_number, auth_code)
    return {"message": "success"}


class Auth(BaseModel):
    phone: str
    code: str


@router.post("/verify")
def verify(auth: Auth):
    phone_number = "".join(filter(str.isdigit, auth.phone))
    auth_code = auth.code
    if redis.get(phone_number) == auth_code:
        return {"message": "success"}
    else:
        return {"message": "fail"}
