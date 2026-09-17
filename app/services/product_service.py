from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product, Category, Unit
from app.schemas.product import ProductCreate, ProductUpdate


def get_product_by_id(
    db: Session,
    product_id: int
) -> Product | None:

    statement = select(Product).where(
        Product.id == product_id
    )

    return db.scalar(statement)


def get_product_by_code(
    db: Session,
    code: str
) -> Product | None:

    statement = select(Product).where(
        Product.code == code
    )

    return db.scalar(statement)


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Product]:

    statement = (
        select(Product)
        .offset(skip)
        .limit(limit)
        .order_by(Product.id.desc())
    )

    return list(db.scalars(statement).all())


def validate_category(
    db: Session,
    category_id: int
) -> Category:

    category = db.scalar(
        select(Category).where(
            Category.id == category_id
        )
    )

    if category is None:
        raise ValueError(
            "Category not found"
        )

    return category


def validate_unit(
    db: Session,
    unit_id: int
) -> Unit:

    unit = db.scalar(
        select(Unit).where(
            Unit.id == unit_id
        )
    )

    if unit is None:
        raise ValueError(
            "Unit not found"
        )

    return unit


def create_product(
    db: Session,
    product_data: ProductCreate
) -> Product:

    # 1. Kiểm tra mã sản phẩm
    existing_product = get_product_by_code(
        db,
        product_data.code
    )

    if existing_product:
        raise ValueError(
            "Product code already exists"
        )

    # 2. Kiểm tra Category
    validate_category(
        db,
        product_data.category_id
    )

    # 3. Kiểm tra Unit
    validate_unit(
        db,
        product_data.unit_id
    )

    # 4. Tạo Product
    product = Product(
        code=product_data.code,
        name=product_data.name,
        category_id=product_data.category_id,
        unit_id=product_data.unit_id,
        product_type=product_data.product_type.value,
        description=product_data.description,
        min_stock=product_data.min_stock,
        is_active=True
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update_product(
    db: Session,
    product: Product,
    product_data: ProductUpdate
) -> Product:

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    # 1. Nếu thay đổi code
    if "code" in update_data:

        existing_product = get_product_by_code(
            db,
            update_data["code"]
        )

        if (
            existing_product
            and existing_product.id != product.id
        ):
            raise ValueError(
                "Product code already exists"
            )

    # 2. Nếu thay đổi Category
    if "category_id" in update_data:

        validate_category(
            db,
            update_data["category_id"]
        )

    # 3. Nếu thay đổi Unit
    if "unit_id" in update_data:

        validate_unit(
            db,
            update_data["unit_id"]
        )

    # 4. Convert Enum thành string
    if "product_type" in update_data:

        update_data["product_type"] = (
            update_data["product_type"].value
        )

    # 5. Update object
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def deactivate_product(
    db: Session,
    product: Product
) -> Product:

    product.is_active = False

    db.commit()
    db.refresh(product)

    return product