from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.warehouse import Warehouse
from app.models.user import User
from app.schemas.stock_movement import (
    StockMovementCreate,
    StockMovementType
)


def get_stock_movement_by_id(
    db: Session,
    movement_id: int
) -> StockMovement | None:

    statement = select(StockMovement).where(
        StockMovement.id == movement_id
    )

    return db.scalar(statement)


def get_stock_movements(
    db: Session,
    warehouse_id: int | None = None,
    product_id: int | None = None,
    movement_type: str | None = None,
    skip: int = 0,
    limit: int = 100
) -> list[StockMovement]:

    statement = select(StockMovement)

    if warehouse_id is not None:
        statement = statement.where(
            StockMovement.warehouse_id == warehouse_id
        )

    if product_id is not None:
        statement = statement.where(
            StockMovement.product_id == product_id
        )

    if movement_type is not None:
        statement = statement.where(
            StockMovement.movement_type == movement_type
        )

    statement = (
        statement
        .offset(skip)
        .limit(limit)
        .order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def create_stock_movement(
    db: Session,
    movement_data: StockMovementCreate,
    current_user: User
) -> StockMovement:

    # --------------------------------------------------
    # 1. Validate movement quantity
    # --------------------------------------------------

    quantity_change = movement_data.quantity_change

    if movement_data.movement_type == StockMovementType.IN:

        if quantity_change <= 0:
            raise ValueError(
                "IN movement must have positive quantity"
            )

    elif movement_data.movement_type == StockMovementType.OUT:

        if quantity_change >= 0:
            raise ValueError(
                "OUT movement must have negative quantity"
            )

    elif movement_data.movement_type == StockMovementType.ADJUSTMENT:

        if quantity_change == 0:
            raise ValueError(
                "ADJUSTMENT quantity cannot be zero"
            )

    # --------------------------------------------------
    # 2. Validate warehouse
    # --------------------------------------------------

    warehouse = db.scalar(
        select(Warehouse).where(
            Warehouse.id == movement_data.warehouse_id
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

    # --------------------------------------------------
    # 3. Validate product
    # --------------------------------------------------

    product = db.scalar(
        select(Product).where(
            Product.id == movement_data.product_id
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

    # --------------------------------------------------
    # 4. Get or create inventory
    # --------------------------------------------------

    statement = (
    select(Inventory)
    .where(
        Inventory.warehouse_id == movement_data.warehouse_id,
        Inventory.product_id == movement_data.product_id
    )
    .with_for_update()
)

    inventory = db.scalar(statement)

    if inventory is None:

        inventory = Inventory(
            warehouse_id=movement_data.warehouse_id,
            product_id=movement_data.product_id,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0")
        )

        db.add(inventory)
        db.flush()

    # --------------------------------------------------
    # 5. Validate stock for OUT
    # --------------------------------------------------

    if quantity_change < 0:

        new_quantity = (
            inventory.quantity
            + quantity_change
        )

        if new_quantity < 0:

            raise ValueError(
                f"Insufficient stock. "
                f"Current stock: {inventory.quantity}"
            )

    # --------------------------------------------------
    # 6. Update inventory
    # --------------------------------------------------

    inventory.quantity = (
        inventory.quantity
        + quantity_change
    )

    # --------------------------------------------------
    # 7. Validate reserved quantity
    # --------------------------------------------------

    if inventory.quantity < inventory.reserved_quantity:

        raise ValueError(
            "Stock quantity cannot be lower "
            "than reserved quantity"
        )

    # --------------------------------------------------
    # 8. Create stock movement
    # --------------------------------------------------

    movement = StockMovement(
        warehouse_id=movement_data.warehouse_id,
        product_id=movement_data.product_id,
        movement_type=movement_data.movement_type.value,
        quantity_change=quantity_change,
        reason=movement_data.reason,
        reference_type=movement_data.reference_type,
        reference_id=movement_data.reference_id,
        created_by=current_user.id
    )

    db.add(movement)

    # --------------------------------------------------
    # 9. Commit everything together
    # --------------------------------------------------

    db.commit()

    db.refresh(movement)

    return movement

def get_stock_movements_by_warehouse(
    db: Session,
    warehouse_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[StockMovement]:

    warehouse = db.scalar(
        select(Warehouse).where(
            Warehouse.id == warehouse_id
        )
    )

    if warehouse is None:
        raise ValueError("Warehouse not found")

    statement = (
        select(StockMovement)
        .where(
            StockMovement.warehouse_id == warehouse_id
        )
        .offset(skip)
        .limit(limit)
        .order_by(StockMovement.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def get_stock_movements_by_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[StockMovement]:

    product = db.scalar(
        select(Product).where(
            Product.id == product_id
        )
    )

    if product is None:
        raise ValueError("Product not found")

    statement = (
        select(StockMovement)
        .where(
            StockMovement.product_id == product_id
        )
        .offset(skip)
        .limit(limit)
        .order_by(StockMovement.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )