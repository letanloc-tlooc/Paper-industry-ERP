from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
)


def generate_order_number(db: Session) -> str:
    last_order = db.scalar(
        select(PurchaseOrder)
        .order_by(PurchaseOrder.id.desc())
    )

    next_id = 1 if last_order is None else last_order.id + 1

    return f"PO-{next_id:05d}"


def get_purchase_order_by_id(
    db: Session,
    purchase_order_id: int
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
    limit: int = 100
) -> list[PurchaseOrder]:

    statement = (
        select(PurchaseOrder)
        .offset(skip)
        .limit(limit)
        .order_by(PurchaseOrder.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def create_purchase_order(
    db: Session,
    data: PurchaseOrderCreate,
    current_user: User
) -> PurchaseOrder:

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

    if not data.items:
        raise ValueError(
            "Purchase order must contain at least one item"
        )

    product_ids = {
        item.product_id
        for item in data.items
    }

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

    order = PurchaseOrder(
        order_number=generate_order_number(db),
        supplier_id=data.supplier_id,
        status="DRAFT",
        order_date=datetime.utcnow(),
        expected_date=data.expected_date,
        note=data.note,
        created_by=current_user.id
    )

    db.add(order)
    db.flush()

    for item in data.items:

        order_item = PurchaseOrderItem(
            purchase_order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            received_quantity=0
        )

        db.add(order_item)

    db.commit()
    db.refresh(order)

    return order