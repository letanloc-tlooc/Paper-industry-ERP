from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category_by_id(
    db: Session,
    category_id: int
) -> Category | None:

    return db.scalar(
        select(Category).where(Category.id == category_id)
    )


def get_category_by_name(
    db: Session,
    name: str
) -> Category | None:

    return db.scalar(
        select(Category).where(Category.name == name)
    )


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Category]:

    statement = (
        select(Category)
        .offset(skip)
        .limit(limit)
        .order_by(Category.id.desc())
    )

    return list(db.scalars(statement).all())


def create_category(
    db: Session,
    category_data: CategoryCreate
) -> Category:

    existing = get_category_by_name(
        db,
        category_data.name
    )

    if existing:
        raise ValueError("Category name already exists")

    category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def update_category(
    db: Session,
    category: Category,
    category_data: CategoryUpdate
) -> Category:

    update_data = category_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        existing = get_category_by_name(
            db,
            update_data["name"]
        )

        if existing and existing.id != category.id:
            raise ValueError("Category name already exists")

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category


def deactivate_category(
    db: Session,
    category: Category
) -> Category:

    # Hiện tại Category chưa có is_active.
    # Vì vậy chưa deactivate ở bước này.
    raise ValueError(
        "Category deactivation is not implemented yet"
    )