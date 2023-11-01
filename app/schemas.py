from datetime import date, time, timedelta, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):  # 사용자 정보
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    phone_number: str = Field(unique=True)  # 01053595167
    username: str  # 권라연
    card_number: str  # 4242-4242-4242-4242
    notification: bool = Field(default=True)  # 알림 여부


class LocationBookmark(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    location_name: str  # 하나고등학교
    location_address: str  # 서울특별시 은평구 연서로 535
    location_poi: int  # 12345678


class DRTBus(SQLModel, table=True):  # DRT 운행 버스 정보 (e.g. DRT 강남 3호차)
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    drt_region: str  # 강남
    drt_route: int  # 3호차
    capacity: int  # 10


class DRTReservation(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    drt_id: UUID  # 배차 DRT 인덱스
    date: date  # 탑승 일자
    time: time  # 탑승 시간
    start_poi: float  # 탑승 위치
    end_poi: float  # 하차 위치
    estimated_time: timedelta  # 예상 소요 시간
    saved_time: str  # 기존 대중교통 대비 절약 시간
    estimate_fee: int  # 예상 요금
    created_at: datetime = Field(default_factory=datetime.utcnow)
