from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate
)


def get_supplier_by_id(
    db: Session,
    supplier_id: int
) -> Supplier | None:

    statement = select(Supplier).where(
        Supplier.id == supplier_id
    )

    return db.scalar(statement)


def get_supplier_by_code(
    db: Session,
    code: str
) -> Supplier | None:

    statement = select(Supplier).where(
        Supplier.code == code
    )

    return db.scalar(statement)


def get_suppliers(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Supplier]:

    statement = (
        select(Supplier)
        .offset(skip)
        .limit(limit)
        .order_by(Supplier.id.desc())
    )

    return list(
        db.scalars(statement).all()
    )


def create_supplier(
    db: Session,
    supplier_data: SupplierCreate
) -> Supplier:

    existing = get_supplier_by_code(
        db,
        supplier_data.code
    )

    if existing:
        raise ValueError(
            "Supplier code already exists"
        )

    supplier = Supplier(
        code=supplier_data.code,
        name=supplier_data.name,
        tax_code=supplier_data.tax_code,
        phone=supplier_data.phone,
        email=supplier_data.email,
        address=supplier_data.address,
        is_active=True
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


def update_supplier(
    db: Session,
    supplier: Supplier,
    supplier_data: SupplierUpdate
) -> Supplier:

    update_data = supplier_data.model_dump(
        exclude_unset=True
    )

    if "code" in update_data:

        existing = get_supplier_by_code(
            db,
            update_data["code"]
        )

        if existing and existing.id != supplier.id:
            raise ValueError(
                "Supplier code already exists"
            )

    for field, value in update_data.items():
        setattr(
            supplier,
            field,
            value
        )

    db.commit()
    db.refresh(supplier)

    return supplier


def deactivate_supplier(
    db: Session,
    supplier: Supplier
) -> Supplier:

    if not supplier.is_active:
        raise ValueError(
            "Supplier is already inactive"
        )

    supplier.is_active = False

    db.commit()
    db.refresh(supplier)

    return supplier