from datetime import date, time, timedelta

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.schemas import User, DRTReservation, LocationBookmark

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


class UserCreate(BaseModel):
    phone_number: str
    username: str
    card_number: str
    notification: bool = True


@router.post("/")
def create_user(user: UserCreate):
    user.phone_number = "".join(filter(str.isdigit, user.phone_number))
    new_user = User.from_orm(user)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "success", "user_id": new_user.id}


@router.get("/{user_id}")
def get_user(user_id: str):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement)
        user = result.first()
        return {"message": "success", "user": user}


@router.put("/{user_id}")
def update_user(user_id: str, user: UserCreate):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement)
        old_user = result.first()
        old_user.username = user.username
        old_user.card_number = user.card_number
        old_user.notification = user.notification
        session.add(old_user)
        session.commit()
        session.refresh(old_user)
        return {"message": "success", "user": old_user}


@router.delete("/{user_id}")
def delete_user(user_id: str):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement)
        old_user = result.first()
        session.delete(old_user)
        session.commit()
        return {"message": "success"}


class LocationBookmarkCreate(BaseModel):
    location_name: str  # 하나고등학교
    location_address: str  # 서울특별시 은평구 연서로 535
    location_poi: int  # 12345678


@router.post("/{user_id}/bookmarks")
def create_bookmark(user_id: str, bookmark: LocationBookmarkCreate):
    bookmark.user_id = user_id
    new_bookmark = LocationBookmark.from_orm(bookmark)
    with Session(engine) as session:
        session.add(new_bookmark)
        session.commit()
        session.refresh(new_bookmark)
        return {"message": "success", "bookmark_id": new_bookmark.id}


class DRTReservationCreate(BaseModel):
    bus_id: str
    date: date
    time: time
    start_poi: float
    end_poi: float
    estimated_time: timedelta
    saved_time: str
    estimate_fee: int


@router.post("/{user_id}/reservations")
def create_reservation(user_id: str, reservation: DRTReservationCreate):
    reservation.user_id = user_id
    new_reservation = DRTReservation.from_orm(reservation)
    with Session(engine) as session:
        session.add(new_reservation)
        session.commit()
        session.refresh(new_reservation)
        return {"message": "success", "reservation_id": new_reservation.id}


@router.get("/{user_id}/bookmarks")
def get_bookmark(user_id: str):
    with Session(engine) as session:
        statement = select(LocationBookmark).where(LocationBookmark.user_id == user_id)
        result = session.exec(statement)
        bookmarks = result.all()
        return {"message": "success", "bookmarks": bookmarks}


@router.get("/{user_id}/reservations")
def get_reservation(user_id: str):
    with Session(engine) as session:
        statement = select(DRTReservation).where(DRTReservation.user_id == user_id)
        result = session.exec(statement)
        reservations = result.all()
        return {"message": "success", "reservations": reservations}
