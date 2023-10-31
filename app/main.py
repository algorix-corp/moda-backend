from os import getenv

import redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import schemas

app = FastAPI(title="MODA API")
load_dotenv()

cors_origin = [
    "http://localhost:5173",
    "https://dev.ride.moda",
    "https://ride.moda",
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
    schemas.get_engine()

    # noinspection PyGlobalUndefined
    global redis_client
    redis_client = redis.Redis(
        host=getenv("REDIS_HOST"),
        port=getenv("REDIS_PORT"),
        password=getenv("REDIS_PASSWORD"),
        decode_responses=True,
    )


@app.on_event("shutdown")
def on_shutdown():
    redis_client.close()


@app.get("/")
def root():
    return {f"message": f"Hello, World! from {getenv('HOSTNAME')}"}
