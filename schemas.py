from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    phone_number: str = Field(unique=True)
    username: str
    card_number: str


class DRTBus(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    drt_region: str  # 서울
    drt_time: int  # 3호차


class LocationBookmark(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    location_name: str
    location_poi: int


class DRTReservation(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    date: str
    time: str
    start_poi: int
    end_poi: int
    bus_id: UUID
    estimated_time: str
    saved_time: str
    estimate_fee: int
