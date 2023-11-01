from app.schemas import DRTBus
from app.database import engine
from sqlmodel import Session, select

with Session(engine) as session:
    bus1 = DRTBus(
        drt_region="강남",
        drt_route="1",
        capacity=10,
    )

    bus2 = DRTBus(
        drt_region="강남",
        drt_route="2",
        capacity=10,
    )

    bus3 = DRTBus(
        drt_region="강남",
        drt_route="3",
        capacity=10,
    )

    bus4 = DRTBus(
        drt_region="은평",
        drt_route="1",
        capacity=10,
    )

    bus5 = DRTBus(
        drt_region="은평",
        drt_route="2",
        capacity=10,
    )

    bus6 = DRTBus(
        drt_region="은평",
        drt_route="3",
        capacity=10,
    )

    bus7 = DRTBus(
        drt_region="노원",
        drt_route="1",
        capacity=10,
    )

    bus8 = DRTBus(
        drt_region="노원",
        drt_route="2",
        capacity=10,
    )

    bus9 = DRTBus(
        drt_region="노원",
        drt_route="3",
        capacity=10,
    )

    bus10 = DRTBus(
        drt_region="평촌",
        drt_route="1",
        capacity=10,
    )

    bus11 = DRTBus(
        drt_region="평촌",
        drt_route="2",
        capacity=10,
    )

    bus12 = DRTBus(
        drt_region="평촌",
        drt_route="3",
        capacity=10,
    )

    bus13 = DRTBus(
        drt_region="당감",
        drt_route="1",
        capacity=10,
    )

    bus14 = DRTBus(
        drt_region="당감",
        drt_route="2",
        capacity=10,
    )

    bus15 = DRTBus(
        drt_region="당감",
        drt_route="3",
        capacity=10,
    )

    session.add(bus1)
    session.add(bus2)
    session.add(bus3)
    session.add(bus4)
    session.add(bus5)
    session.add(bus6)
    session.add(bus7)
    session.add(bus8)
    session.add(bus9)
    session.add(bus10)
    session.add(bus11)
    session.add(bus12)
    session.add(bus13)
    session.add(bus14)
    session.add(bus15)

    session.commit()
