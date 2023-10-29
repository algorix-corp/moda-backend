from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    phone: str
    password: str
    name: str


class Dropzone(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    poi_id: str
    lat: float
    lon: float
    description: str


class DRTReservation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    dropzone_id: UUID
    loc_x: float
    loc_y: float
    direction: str
    start_time: datetime
