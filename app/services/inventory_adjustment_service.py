from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.warehouse import Warehouse
from app.schemas.inventory_adjustment import InventoryAdjustmentCreate


def adjust_inventory(
    db: Session,
    data: InventoryAdjustmentCreate,
    current_user_id: int | None = None,
) -> Inventory:

    # --------------------------------
    # Validate quantity_change
    # --------------------------------
    if data.quantity_change == 0:
        raise ValueError(
            "quantity_change must not be zero"
        )

    # --------------------------------
    # Validate warehouse
    # --------------------------------
    warehouse = db.scalar(
        select(Warehouse).where(
            Warehouse.id == data.warehouse_id
        )
    )

    if warehouse is None:
        raise ValueError(
            "Warehouse not found"
        )

    if not warehouse.is_active:
        raise ValueError(
            "Warehouse is inactive"
        )

    # --------------------------------
    # Validate product
    # --------------------------------
    product = db.scalar(
        select(Product).where(
            Product.id == data.product_id
        )
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    if not product.is_active:
        raise ValueError(
            "Product is inactive"
        )

    # --------------------------------
    # Find inventory
    # --------------------------------
    inventory = db.scalar(
        select(Inventory).where(
            Inventory.warehouse_id == data.warehouse_id,
            Inventory.product_id == data.product_id,
        )
    )

    # --------------------------------
    # Create inventory if not exists
    # --------------------------------
    if inventory is None:

        if data.quantity_change < 0:
            raise ValueError(
                "Cannot decrease inventory that does not exist"
            )

        inventory = Inventory(
            warehouse_id=data.warehouse_id,
            product_id=data.product_id,
            quantity=0,
            reserved_quantity=0,
        )

        db.add(inventory)
        db.flush()

    # --------------------------------
    # Check available quantity
    # --------------------------------
    new_quantity = (
        inventory.quantity
        + data.quantity_change
    )

    if new_quantity < 0:
        raise ValueError(
            "Inventory quantity cannot be negative"
        )

    if new_quantity < inventory.reserved_quantity:
        raise ValueError(
            "Inventory quantity cannot be lower "
            "than reserved quantity"
        )

    # --------------------------------
    # Update inventory
    # --------------------------------
    inventory.quantity = new_quantity

    # --------------------------------
    # Create stock movement
    # --------------------------------
    movement = StockMovement(
        warehouse_id=data.warehouse_id,
        product_id=data.product_id,
        movement_type="ADJUSTMENT",
        quantity_change=data.quantity_change,
        reason=data.reason,
        reference_type="INVENTORY_ADJUSTMENT",
        reference_id=inventory.id,
        created_by=current_user_id,
    )

    db.add(movement)

    db.commit()

    db.refresh(inventory)

    return inventory