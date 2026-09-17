from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    products = relationship(
        "Product",
        back_populates="category"
    )


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    products = relationship(
        "Product",
        back_populates="unit"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categories.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    unit_id: Mapped[int] = mapped_column(
        ForeignKey(
            "units.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    product_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    min_stock: Mapped[float] = mapped_column(
        Numeric(15, 3),
        default=0,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    unit = relationship(
        "Unit",
        back_populates="products"
    )
    inventories = relationship(
        "Inventory",
        back_populates="product"
    )

    stock_movements = relationship(
        "StockMovement",
        back_populates="product"
    )