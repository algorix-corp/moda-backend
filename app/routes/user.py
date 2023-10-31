from fastapi import APIRouter, Depends

import app.dependencies as dependencies

router = APIRouter(
    prefix="/user",
    tags=["User"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={404: {"description": "Not found"}},
)
