from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.stock_movement import StockMovement


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

def reserve_stock(
    db: Session,
    warehouse_id: int,
    product_id: int,
    quantity: Decimal,
) -> Inventory:

    if quantity <= 0:
        raise ValueError("Reserve quantity must be greater than 0")

    try:
        # 1. Kiểm tra Warehouse
        warehouse = db.get(Warehouse, warehouse_id)

        if warehouse is None:
            raise ValueError("Warehouse not found")

        if not warehouse.is_active:
            raise ValueError("Warehouse is inactive")

        # 2. Kiểm tra Product
        product = db.get(Product, product_id)

        if product is None:
            raise ValueError("Product not found")

        if not product.is_active:
            raise ValueError("Product is inactive")

        # 3. Lấy Inventory và khóa bản ghi
        statement = (
            select(Inventory)
            .where(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
            )
            .with_for_update()
        )

        inventory = db.scalar(statement)

        if inventory is None:
            raise ValueError("Inventory not found")

        # 4. Kiểm tra số lượng khả dụng
        if inventory.available_quantity < quantity:
            raise ValueError(
                f"Insufficient available stock. "
                f"Available: {inventory.available_quantity}, "
                f"Requested: {quantity}"
            )

        # 5. Reserve
        inventory.reserved_quantity += quantity

        # 6. Lưu database
        db.commit()
        db.refresh(inventory)

        return inventory

    except Exception:
        db.rollback()
        raise

def release_stock(
    db: Session,
    warehouse_id: int,
    product_id: int,
    quantity: Decimal,
) -> Inventory:

    if quantity <= 0:
        raise ValueError("Release quantity must be greater than 0")

    try:
        warehouse = db.get(Warehouse, warehouse_id)

        if warehouse is None:
            raise ValueError("Warehouse not found")

        if not warehouse.is_active:
            raise ValueError("Warehouse is inactive")

        product = db.get(Product, product_id)

        if product is None:
            raise ValueError("Product not found")

        if not product.is_active:
            raise ValueError("Product is inactive")

        statement = (
            select(Inventory)
            .where(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
            )
            .with_for_update()
        )

        inventory = db.scalar(statement)

        if inventory is None:
            raise ValueError("Inventory not found")

        if inventory.reserved_quantity < quantity:
            raise ValueError(
                f"Insufficient reserved stock. "
                f"Reserved: {inventory.reserved_quantity}, "
                f"Requested: {quantity}"
            )

        inventory.reserved_quantity -= quantity

        db.commit()
        db.refresh(inventory)

        return inventory

    except Exception:
        db.rollback()
        raise

def stock_out(
    db: Session,
    warehouse_id: int,
    product_id: int,
    quantity: Decimal,
    reason: str | None = None,
    reference_type: str | None = None,
    reference_id: int | None = None,
    current_user_id: int | None = None,
) -> Inventory:

    if quantity <= 0:
        raise ValueError(
            "Stock out quantity must be greater than 0"
        )

    try:
        # 1. Check warehouse
        warehouse = db.get(
            Warehouse,
            warehouse_id
        )

        if warehouse is None:
            raise ValueError(
                "Warehouse not found"
            )

        if not warehouse.is_active:
            raise ValueError(
                "Warehouse is inactive"
            )

        # 2. Check product
        product = db.get(
            Product,
            product_id
        )

        if product is None:
            raise ValueError(
                "Product not found"
            )

        if not product.is_active:
            raise ValueError(
                "Product is inactive"
            )

        # 3. Lock inventory row
        statement = (
            select(Inventory)
            .where(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
            )
            .with_for_update()
        )

        inventory = db.scalar(statement)

        if inventory is None:
            raise ValueError(
                "Inventory not found"
            )

        # 4. Check physical stock
        if inventory.quantity < quantity:
            raise ValueError(
                f"Insufficient stock. "
                f"Stock: {inventory.quantity}, "
                f"Requested: {quantity}"
            )

        # 5. Check reserved stock
        if inventory.reserved_quantity < quantity:
            raise ValueError(
                f"Insufficient reserved stock. "
                f"Reserved: {inventory.reserved_quantity}, "
                f"Requested: {quantity}"
            )

        # 6. Update inventory
        inventory.quantity -= quantity
        inventory.reserved_quantity -= quantity

        # 7. Create stock movement
        movement = StockMovement(
            warehouse_id=warehouse_id,
            product_id=product_id,
            movement_type="OUT",
            quantity_change=-quantity,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
            created_by=current_user_id,
        )

        db.add(movement)

        # 8. Commit everything together
        db.commit()

        db.refresh(inventory)

        return inventory

    except Exception:
        db.rollback()
        raise