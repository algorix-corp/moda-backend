from os import getenv

import redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import create_engine

from schemas import *

app = FastAPI(title="MODA API")
load_dotenv()

cors_origin = [
    "http://localhost:5173",
    "https://dev.ride.moda",
    "https://ride.moda",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    global redis_client, engine

    redis_client = redis.Redis(
        host=getenv("REDIS_HOST"),
        port=getenv("REDIS_PORT"),
        password=getenv("REDIS_PASSWORD"),
        decode_responses=True,
    )

    databaseUrl = (f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}"
                   f"@{getenv('POSTGRES_HOST')}:{getenv('POSTGRES_PORT')}/{getenv('POSTGRES_DB')}")

    engine = create_engine(databaseUrl, echo=True)
    SQLModel.metadata.create_all(engine)
