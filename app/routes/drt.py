from datetime import date, time, timedelta

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.schemas import DRTReservation, DRTBus

router = APIRouter(
    prefix="/drt",
    tags=["DRT"],
)


class DRTReservationCreate(BaseModel):
    user_id: str
    bus_id: str
    date: date
    time: time
    start_poi: float
    end_poi: float
    estimated_time: timedelta
    saved_time: str
    estimate_fee: int


@router.post("/")
def create_drt_reservation(drt_reservation: DRTReservationCreate):
    new_drt_reservation = DRTReservation.from_orm(drt_reservation)
    with Session(engine) as session:
        session.add(new_drt_reservation)
        session.commit()
        session.refresh(new_drt_reservation)
        return {"message": "success", "drt_reservation_id": new_drt_reservation.id}


@router.get("/{drt_reservation_id}")
def get_drt_reservation(drt_reservation_id: str):
    with Session(engine) as session:
        statement = select(DRTReservation).where(DRTReservation.id == drt_reservation_id)
        result = session.exec(statement)
        drt_reservation = result.first()
        return {"message": "success", "drt_reservation": drt_reservation}


@router.get("/dist_drt/")
def get_regions():
    with Session(engine) as session:
        statement = select(DRTBus).distinct()
        result = session.exec(statement)
        regions = result.all()
        return {"message": "success", "regions": regions}


@router.get("/dist_drt/{region}")
def get_dist_drt(region: str):
    with Session(engine) as session:
        statement = select(DRTReservation).where(DRTReservation.drt_region == region)
        result = session.exec(statement)
        drt_reservations = result.all()
        return {"message": "success", "drt_reservations": drt_reservations}


@router.put("/{drt_reservation_id}")
def update_drt_reservation(drt_reservation_id: str, drt_reservation: DRTReservationCreate):
    with Session(engine) as session:
        statement = select(DRTReservation).where(DRTReservation.id == drt_reservation_id)
        result = session.exec(statement)
        old_drt_reservation = result.first()
        old_drt_reservation.user_id = drt_reservation.user_id
        old_drt_reservation.bus_id = drt_reservation.bus_id
        old_drt_reservation.date = drt_reservation.date
        old_drt_reservation.time = drt_reservation.time
        old_drt_reservation.start_poi = drt_reservation.start_poi
        old_drt_reservation.end_poi = drt_reservation.end_poi
        old_drt_reservation.estimated_time = drt_reservation.estimated_time
        old_drt_reservation.saved_time = drt_reservation.saved_time
        old_drt_reservation.estimate_fee = drt_reservation.estimate_fee
        session.add(old_drt_reservation)
        session.commit()
        session.refresh(old_drt_reservation)
        return {"message": "success", "drt_reservation": old_drt_reservation}


@router.delete("/{drt_reservation_id}")
def delete_drt_reservation(drt_reservation_id: str):
    with Session(engine) as session:
        statement = select(DRTReservation).where(DRTReservation.id == drt_reservation_id)
        result = session.exec(statement)
        old_drt_reservation = result.first()
        session.delete(old_drt_reservation)
        session.commit()
        return {"message": "success"}
