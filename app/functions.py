from datetime import datetime, timedelta
from os import getenv

import jwt
from dotenv import load_dotenv

import app.schemas as schemas

load_dotenv()


def generate_jwt_token(user: schemas.User):
    to_encode = user.dict()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, getenv("JWT_SECRET"), algorithm="HS256")
    return encoded_jwt
