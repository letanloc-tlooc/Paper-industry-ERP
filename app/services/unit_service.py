from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Unit
from app.schemas.unit import UnitCreate, UnitUpdate


def get_unit_by_id(
    db: Session,
    unit_id: int
) -> Unit | None:

    return db.scalar(
        select(Unit).where(Unit.id == unit_id)
    )


def get_unit_by_name(
    db: Session,
    name: str
) -> Unit | None:

    return db.scalar(
        select(Unit).where(Unit.name == name)
    )


def get_units(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Unit]:

    statement = (
        select(Unit)
        .offset(skip)
        .limit(limit)
        .order_by(Unit.id.desc())
    )

    return list(db.scalars(statement).all())


def create_unit(
    db: Session,
    unit_data: UnitCreate
) -> Unit:

    existing_name = get_unit_by_name(
        db,
        unit_data.name
    )

    if existing_name:
        raise ValueError("Unit name already exists")

    existing_symbol = db.scalar(
        select(Unit).where(
            Unit.symbol == unit_data.symbol
        )
    )

    if existing_symbol:
        raise ValueError("Unit symbol already exists")

    unit = Unit(
        name=unit_data.name,
        symbol=unit_data.symbol
    )

    db.add(unit)
    db.commit()
    db.refresh(unit)

    return unit


def update_unit(
    db: Session,
    unit: Unit,
    unit_data: UnitUpdate
) -> Unit:

    update_data = unit_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:

        existing_name = get_unit_by_name(
            db,
            update_data["name"]
        )

        if existing_name and existing_name.id != unit.id:
            raise ValueError("Unit name already exists")

    if "symbol" in update_data:

        existing_symbol = db.scalar(
            select(Unit).where(
                Unit.symbol == update_data["symbol"]
            )
        )

        if existing_symbol and existing_symbol.id != unit.id:
            raise ValueError("Unit symbol already exists")

    for field, value in update_data.items():
        setattr(unit, field, value)

    db.commit()
    db.refresh(unit)

    return unit