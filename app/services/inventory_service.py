from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse


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

def get_inventory_by_warehouse(
    db: Session,
    warehouse_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Inventory]:

    warehouse = db.scalar(
        select(Warehouse).where(
            Warehouse.id == warehouse_id
        )
    )

    if warehouse is None:
        raise ValueError("Warehouse not found")

    statement = (
        select(Inventory)
        .where(
            Inventory.warehouse_id == warehouse_id
        )
        .offset(skip)
        .limit(limit)
        .order_by(Inventory.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def get_inventory_by_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Inventory]:

    product = db.scalar(
        select(Product).where(
            Product.id == product_id
        )
    )

    if product is None:
        raise ValueError("Product not found")

    statement = (
        select(Inventory)
        .where(
            Inventory.product_id == product_id
        )
        .offset(skip)
        .limit(limit)
        .order_by(Inventory.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def get_inventory_by_warehouse_and_product(
    db: Session,
    warehouse_id: int,
    product_id: int,
) -> Inventory | None:

    warehouse = db.scalar(
        select(Warehouse).where(
            Warehouse.id == warehouse_id
        )
    )

    if warehouse is None:
        raise ValueError("Warehouse not found")

    product = db.scalar(
        select(Product).where(
            Product.id == product_id
        )
    )

    if product is None:
        raise ValueError("Product not found")

    return db.scalar(
        select(Inventory).where(
            Inventory.warehouse_id == warehouse_id,
            Inventory.product_id == product_id,
        )
    )