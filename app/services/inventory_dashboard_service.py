from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.warehouse import Warehouse


def get_inventory_dashboard(
    db: Session,
    warehouse_id: int | None = None,
):
    # -----------------------------------------
    # 1. Validate warehouse
    # -----------------------------------------

    if warehouse_id is not None:
        warehouse = db.scalar(
            select(Warehouse).where(
                Warehouse.id == warehouse_id
            )
        )

        if warehouse is None:
            raise ValueError("Warehouse not found")

    # -----------------------------------------
    # 2. Inventory statistics
    # -----------------------------------------

    inventory_statement = select(
        func.count(Inventory.id),
        func.coalesce(
            func.sum(Inventory.quantity),
            Decimal("0")
        ),
        func.coalesce(
            func.sum(Inventory.reserved_quantity),
            Decimal("0")
        ),
        func.coalesce(
            func.sum(
                Inventory.quantity
                - Inventory.reserved_quantity
            ),
            Decimal("0")
        ),
    )

    if warehouse_id is not None:
        inventory_statement = inventory_statement.where(
            Inventory.warehouse_id == warehouse_id
        )

    (
        total_inventory_items,
        total_quantity,
        total_reserved_quantity,
        total_available_quantity,
    ) = db.execute(inventory_statement).one()

    # -----------------------------------------
    # 3. Low-stock count
    # -----------------------------------------

    low_stock_statement = (
        select(func.count(Inventory.id))
        .join(
            Product,
            Product.id == Inventory.product_id,
        )
        .where(
            Product.is_active.is_(True),
            (
                Inventory.quantity
                - Inventory.reserved_quantity
            ) <= Product.min_stock,
        )
    )

    if warehouse_id is not None:
        low_stock_statement = low_stock_statement.where(
            Inventory.warehouse_id == warehouse_id
        )

    low_stock_items = db.scalar(
        low_stock_statement
    ) or 0

    # -----------------------------------------
    # 4. Stock movement statistics
    # -----------------------------------------

    movement_statement = (
        select(
            StockMovement.movement_type,
            func.coalesce(
                func.sum(
                    StockMovement.quantity_change
                ),
                Decimal("0"),
            ),
        )
        .group_by(
            StockMovement.movement_type
        )
    )

    if warehouse_id is not None:
        movement_statement = movement_statement.where(
            StockMovement.warehouse_id == warehouse_id
        )

    movement_rows = db.execute(
        movement_statement
    ).all()

    movement_summary = {
        "IN": Decimal("0"),
        "OUT": Decimal("0"),
        "ADJUSTMENT": Decimal("0"),
    }

    for movement_type, total in movement_rows:
        if movement_type in movement_summary:
            movement_summary[movement_type] = total

    # -----------------------------------------
    # 5. Return dashboard
    # -----------------------------------------

    return {
        "total_inventory_items": total_inventory_items,
        "total_quantity": total_quantity,
        "total_reserved_quantity": total_reserved_quantity,
        "total_available_quantity": total_available_quantity,
        "low_stock_items": low_stock_items,
        "movement_summary": movement_summary,
    }