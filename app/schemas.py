from datetime import date, time, timedelta, datetime
from os import getenv
from typing import Optional
from uuid import UUID, uuid4

from dotenv import load_dotenv
from sqlmodel import SQLModel, Field, create_engine

engine = None
load_dotenv()


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
    drt_time: int  # 3호차
    drt_start_time: str  # 08:00  (운행 시작 시간)
    drt_end_time: str  # 20:00  (운행 종료 시간)
    drt_day: str  # [MON, TUE, WED, THU, FRI, SAT, SUN]  (운행 요일)


class DRTReservation(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    drt_id: UUID  # 배차 DRT 인덱스
    date: date  # 탑승 일자
    time: time  # 탑승 시간
    start_poi: int  # 탑승 위치
    end_poi: int  # 하차 위치
    estimated_time: timedelta  # 예상 소요 시간
    saved_time: str  # 기존 대중교통 대비 절약 시간
    estimate_fee: int  # 예상 요금
    created_at: datetime = Field(default_factory=datetime.utcnow)


def get_engine():
    global engine
    if engine is None:
        database_url = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}" \
                       f"@{getenv('POSTGRES_HOST')}:{getenv('POSTGRES_PORT')}/{getenv('POSTGRES_DB')}"
        engine = create_engine(database_url, echo=True)
        SQLModel.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    get_engine()
