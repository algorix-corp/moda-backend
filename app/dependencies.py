import os

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas import User

JWT_SECRET = os.getenv("JWT_SECRET")


def get_token_header(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        data = User(**jwt.decode(token.credentials, JWT_SECRET, algorithms=["HS256"]))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="인증하는데 문제가 발생했어요.")
    return data
