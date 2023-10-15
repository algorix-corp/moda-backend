from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

SECRET_KEY = "e8a2a72e5dd676288027565e2ada4758"
ALGORITHM = "HS256"


def get_token_data(token: str = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def issue_token(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
