from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.database import engine
from app.routes import auth, user, drt, map

app = FastAPI(title="MODA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(drt.router)
app.include_router(map.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
