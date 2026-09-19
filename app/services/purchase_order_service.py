from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderReceive,
    PurchaseOrderUpdate,
)


# ============================================================
# Generate Purchase Order Number
# ============================================================

def generate_order_number(db: Session) -> str:

    last_order = db.scalar(
        select(PurchaseOrder)
        .order_by(PurchaseOrder.id.desc())
    )

    next_id = (
        1
        if last_order is None
        else last_order.id + 1
    )

    return f"PO-{next_id:05d}"


# ============================================================
# Get Purchase Order
# ============================================================

def get_purchase_order_by_id(
    db: Session,
    purchase_order_id: int,
) -> PurchaseOrder | None:

    return db.scalar(
        select(PurchaseOrder)
        .where(
            PurchaseOrder.id == purchase_order_id
        )
    )


def get_purchase_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[PurchaseOrder]:

    statement = (
        select(PurchaseOrder)
        .offset(skip)
        .limit(limit)
        .order_by(
            PurchaseOrder.id.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# Create Purchase Order
# ============================================================

def create_purchase_order(
    db: Session,
    data: PurchaseOrderCreate,
    current_user: User,
) -> PurchaseOrder:

    # --------------------------------------------------------
    # Validate Supplier
    # --------------------------------------------------------

    supplier = db.scalar(
        select(Supplier)
        .where(
            Supplier.id == data.supplier_id
        )
    )

    if supplier is None:
        raise ValueError(
            "Supplier not found"
        )

    if not supplier.is_active:
        raise ValueError(
            "Supplier is inactive"
        )

    # --------------------------------------------------------
    # Validate Items
    # --------------------------------------------------------

    if not data.items:
        raise ValueError(
            "Purchase order must contain at least one item"
        )

    # --------------------------------------------------------
    # Prevent duplicate products
    # --------------------------------------------------------

    product_ids = [
        item.product_id
        for item in data.items
    ]

    if len(product_ids) != len(set(product_ids)):
        raise ValueError(
            "A product cannot appear multiple times "
            "in the same purchase order"
        )

    # --------------------------------------------------------
    # Load Products
    # --------------------------------------------------------

    products = db.scalars(
        select(Product)
        .where(
            Product.id.in_(product_ids)
        )
    ).all()

    product_map = {
        product.id: product
        for product in products
    }

    # --------------------------------------------------------
    # Validate Products
    # --------------------------------------------------------

    for item in data.items:

        product = product_map.get(
            item.product_id
        )

        if product is None:
            raise ValueError(
                f"Product {item.product_id} not found"
            )

        if not product.is_active:
            raise ValueError(
                f"Product {item.product_id} is inactive"
            )

    # --------------------------------------------------------
    # Create Purchase Order
    # --------------------------------------------------------

    purchase_order = PurchaseOrder(
        order_number=generate_order_number(db),
        supplier_id=data.supplier_id,
        status="DRAFT",
        order_date=datetime.utcnow(),
        expected_date=data.expected_date,
        note=data.note,
        created_by=current_user.id,
    )

    db.add(purchase_order)

    # Generate PO ID
    db.flush()

    # --------------------------------------------------------
    # Create Purchase Order Items
    # --------------------------------------------------------

    for item in data.items:

        purchase_order_item = PurchaseOrderItem(
            purchase_order_id=purchase_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            received_quantity=Decimal("0"),
        )

        db.add(purchase_order_item)

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    db.commit()

    db.refresh(
        purchase_order
    )

    return purchase_order


# ============================================================
# Update Purchase Order
# ============================================================

def update_purchase_order(
    db: Session,
    purchase_order: PurchaseOrder,
    data: PurchaseOrderUpdate,
) -> PurchaseOrder:

    # --------------------------------------------------------
    # Only DRAFT can be updated
    # --------------------------------------------------------

    if purchase_order.status != "DRAFT":
        raise ValueError(
            "Only draft purchase orders can be updated"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Validate Supplier
    # --------------------------------------------------------

    if "supplier_id" in update_data:

        supplier = db.scalar(
            select(Supplier)
            .where(
                Supplier.id == update_data["supplier_id"]
            )
        )

        if supplier is None:
            raise ValueError(
                "Supplier not found"
            )

        if not supplier.is_active:
            raise ValueError(
                "Supplier is inactive"
            )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    for field, value in update_data.items():

        setattr(
            purchase_order,
            field,
            value
        )

    db.commit()

    db.refresh(
        purchase_order
    )

    return purchase_order


# ============================================================
# Confirm Purchase Order
# ============================================================

def confirm_purchase_order(
    db: Session,
    purchase_order: PurchaseOrder,
) -> PurchaseOrder:

    # --------------------------------------------------------
    # Only DRAFT can be confirmed
    # --------------------------------------------------------

    if purchase_order.status != "DRAFT":
        raise ValueError(
            "Only draft purchase orders can be confirmed"
        )

    # --------------------------------------------------------
    # Validate Items
    # --------------------------------------------------------

    if not purchase_order.items:
        raise ValueError(
            "Purchase order must contain at least one item"
        )

    # --------------------------------------------------------
    # Validate Supplier
    # --------------------------------------------------------

    supplier = db.scalar(
        select(Supplier)
        .where(
            Supplier.id == purchase_order.supplier_id
        )
    )

    if supplier is None:
        raise ValueError(
            "Supplier not found"
        )

    if not supplier.is_active:
        raise ValueError(
            "Supplier is inactive"
        )

    # --------------------------------------------------------
    # Confirm
    # --------------------------------------------------------

    purchase_order.status = "CONFIRMED"

    db.commit()

    db.refresh(
        purchase_order
    )

    return purchase_order


# ============================================================
# Receive Purchase Order
# ============================================================

def receive_purchase_order(
    db: Session,
    purchase_order: PurchaseOrder,
    data: PurchaseOrderReceive,
    current_user: User,
) -> PurchaseOrder:

    if purchase_order.status not in [
        "CONFIRMED",
        "PARTIALLY_RECEIVED",
    ]:
        raise ValueError(
            "Only confirmed or partially received purchase orders can be received"
        )

    if not purchase_order.items:
        raise ValueError(
            "Purchase order has no items"
        )

    # --------------------------------------------------------
    # Validate warehouse
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Map PO items
    # --------------------------------------------------------

    order_items = {
        item.product_id: item
        for item in purchase_order.items
    }

    received_product_ids: set[int] = set()

    # --------------------------------------------------------
    # Validate receive request trước khi thay đổi DB
    # --------------------------------------------------------

    for receive_item in data.items:

        product_id = receive_item.product_id
        receive_quantity = receive_item.quantity

        # Duplicate product
        if product_id in received_product_ids:
            raise ValueError(
                f"Product {product_id} appears multiple times "
                "in receive request"
            )

        received_product_ids.add(product_id)

        # Product không thuộc PO
        order_item = order_items.get(product_id)

        if order_item is None:
            raise ValueError(
                f"Product {product_id} does not belong "
                "to this purchase order"
            )

        # Số lượng còn lại
        remaining_quantity = (
            order_item.quantity
            - order_item.received_quantity
        )

        # Không được nhận quá số lượng
        if receive_quantity > remaining_quantity:
            raise ValueError(
                f"Product {product_id}: cannot receive "
                f"{receive_quantity}. "
                f"Remaining quantity is {remaining_quantity}"
            )

    # --------------------------------------------------------
    # Process receive
    # --------------------------------------------------------

    for receive_item in data.items:

        product_id = receive_item.product_id
        quantity = receive_item.quantity

        order_item = order_items[product_id]

        # Update received quantity
        order_item.received_quantity += quantity

        # ----------------------------------------------------
        # Inventory
        # ----------------------------------------------------

        inventory = db.scalar(
            select(Inventory).where(
                Inventory.warehouse_id == data.warehouse_id,
                Inventory.product_id == product_id,
            )
        )

        if inventory is None:

            inventory = Inventory(
                warehouse_id=data.warehouse_id,
                product_id=product_id,
                quantity=quantity,
                reserved_quantity=Decimal("0"),
            )

            db.add(inventory)

        else:

            inventory.quantity += quantity

        # ----------------------------------------------------
        # Stock Movement
        # ----------------------------------------------------

        movement = StockMovement(
            warehouse_id=data.warehouse_id,
            product_id=product_id,
            movement_type="IN",
            quantity_change=quantity,
            reason="Purchase order receipt",
            reference_type="PURCHASE_ORDER",
            reference_id=purchase_order.id,
            created_by=current_user.id,
        )

        db.add(movement)

    # --------------------------------------------------------
    # Update PO status
    # --------------------------------------------------------

    all_received = all(
        item.received_quantity >= item.quantity
        for item in purchase_order.items
    )

    any_received = any(
        item.received_quantity > Decimal("0")
        for item in purchase_order.items
    )

    if all_received:

        purchase_order.status = "COMPLETED"

    elif any_received:

        purchase_order.status = "PARTIALLY_RECEIVED"

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    db.commit()

    db.refresh(purchase_order)

    return purchase_order


# ============================================================
# Cancel Purchase Order
# ============================================================

def cancel_purchase_order(
    db: Session,
    purchase_order: PurchaseOrder,
) -> PurchaseOrder:

    # --------------------------------------------------------
    # Only DRAFT / CONFIRMED can be cancelled
    # --------------------------------------------------------

    if purchase_order.status not in [
        "DRAFT",
        "CONFIRMED",
    ]:
        raise ValueError(
            "Purchase order cannot be cancelled"
        )

    purchase_order.status = "CANCELLED"

    db.commit()

    db.refresh(
        purchase_order
    )

    return purchase_order


# ============================================================
# Delete Purchase Order
# ============================================================

def delete_purchase_order(
    db: Session,
    purchase_order: PurchaseOrder,
) -> None:

    if purchase_order.status != "DRAFT":
        raise ValueError(
            "Only draft purchase orders can be deleted"
        )

    db.delete(
        purchase_order
    )

    db.commit()

