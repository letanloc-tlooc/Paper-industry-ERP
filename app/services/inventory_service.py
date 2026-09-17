from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory


def get_inventory_by_id(
    db: Session,
    inventory_id: int
) -> Inventory | None:

    statement = select(Inventory).where(
        Inventory.id == inventory_id
    )

    return db.scalar(statement)


def get_inventory(
    db: Session,
    warehouse_id: int,
    product_id: int
) -> Inventory | None:

    statement = select(Inventory).where(
        Inventory.warehouse_id == warehouse_id,
        Inventory.product_id == product_id
    )

    return db.scalar(statement)


def get_inventories(
    db: Session,
    warehouse_id: int | None = None,
    product_id: int | None = None,
    skip: int = 0,
    limit: int = 100
) -> list[Inventory]:

    statement = select(Inventory)

    if warehouse_id is not None:
        statement = statement.where(
            Inventory.warehouse_id == warehouse_id
        )

    if product_id is not None:
        statement = statement.where(
            Inventory.product_id == product_id
        )

    statement = (
        statement
        .offset(skip)
        .limit(limit)
        .order_by(Inventory.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def get_or_create_inventory(
    db: Session,
    warehouse_id: int,
    product_id: int
) -> Inventory:

    inventory = get_inventory(
        db,
        warehouse_id,
        product_id
    )

    if inventory:
        return inventory

    inventory = Inventory(
        warehouse_id=warehouse_id,
        product_id=product_id,
        quantity=Decimal("0"),
        reserved_quantity=Decimal("0")
    )

    db.add(inventory)

    # Flush để SQLAlchemy gửi INSERT
    # nhưng chưa commit transaction.
    db.flush()

    return inventory