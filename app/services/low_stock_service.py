from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse


def get_low_stock_items(
    db: Session,
    warehouse_id: int | None = None,
    product_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    statement = (
        select(
            Inventory,
            Product.code,
            Product.name,
            Product.min_stock,
        )
        .join(
            Product,
            Product.id == Inventory.product_id,
        )
        .join(
            Warehouse,
            Warehouse.id == Inventory.warehouse_id,
        )
        .where(
            Inventory.quantity - Inventory.reserved_quantity
            <= Product.min_stock
        )
    )

    # --------------------------------
    # Filter warehouse
    # --------------------------------
    if warehouse_id is not None:

        warehouse = db.scalar(
            select(Warehouse).where(
                Warehouse.id == warehouse_id
            )
        )

        if warehouse is None:
            raise ValueError(
                "Warehouse not found"
            )

        statement = statement.where(
            Inventory.warehouse_id == warehouse_id
        )

    # --------------------------------
    # Filter product
    # --------------------------------
    if product_id is not None:

        product = db.scalar(
            select(Product).where(
                Product.id == product_id
            )
        )

        if product is None:
            raise ValueError(
                "Product not found"
            )

        statement = statement.where(
            Inventory.product_id == product_id
        )

    # --------------------------------
    # Only active products
    # --------------------------------
    statement = statement.where(
        Product.is_active.is_(True)
    )

    # --------------------------------
    # Pagination
    # --------------------------------
    statement = (
        statement
        .order_by(
            Inventory.id.desc()
        )
        .offset(skip)
        .limit(limit)
    )

    results = db.execute(statement).all()

    return [
        {
            "inventory_id": inventory.id,

            "warehouse_id": inventory.warehouse_id,
            "product_id": inventory.product_id,

            "product_code": product_code,
            "product_name": product_name,

            "min_stock": min_stock,

            "quantity": inventory.quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "available_quantity": (
                inventory.quantity
                - inventory.reserved_quantity
            ),
        }
        for (
            inventory,
            product_code,
            product_name,
            min_stock,
        ) in results
    ]