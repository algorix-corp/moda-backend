from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
import app.schemas as schemas
import app.dependencies as dependencies
import app.functions as functions

router = APIRouter(
    prefix="/user",
    tags=["User"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={404: {"description": "Not found"}},
)
