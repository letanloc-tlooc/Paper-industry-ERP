from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseUpdate
)


def get_warehouse_by_id(
    db: Session,
    warehouse_id: int
) -> Warehouse | None:

    statement = select(Warehouse).where(
        Warehouse.id == warehouse_id
    )

    return db.scalar(statement)


def get_warehouse_by_code(
    db: Session,
    code: str
) -> Warehouse | None:

    statement = select(Warehouse).where(
        Warehouse.code == code
    )

    return db.scalar(statement)


def get_warehouses(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Warehouse]:

    statement = (
        select(Warehouse)
        .offset(skip)
        .limit(limit)
        .order_by(Warehouse.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def create_warehouse(
    db: Session,
    warehouse_data: WarehouseCreate
) -> Warehouse:

    existing = get_warehouse_by_code(
        db,
        warehouse_data.code
    )

    if existing:
        raise ValueError(
            "Warehouse code already exists"
        )

    warehouse = Warehouse(
        code=warehouse_data.code,
        name=warehouse_data.name,
        location=warehouse_data.location,
        is_active=True
    )

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return warehouse


def update_warehouse(
    db: Session,
    warehouse: Warehouse,
    warehouse_data: WarehouseUpdate
) -> Warehouse:

    update_data = warehouse_data.model_dump(
        exclude_unset=True
    )

    if "code" in update_data:

        existing = get_warehouse_by_code(
            db,
            update_data["code"]
        )

        if existing and existing.id != warehouse.id:
            raise ValueError(
                "Warehouse code already exists"
            )

    for field, value in update_data.items():
        setattr(
            warehouse,
            field,
            value
        )

    db.commit()
    db.refresh(warehouse)

    return warehouse


def deactivate_warehouse(
    db: Session,
    warehouse: Warehouse
) -> Warehouse:

    if not warehouse.is_active:
        raise ValueError(
            "Warehouse is already inactive"
        )

    warehouse.is_active = False

    db.commit()
    db.refresh(warehouse)

    return warehouse