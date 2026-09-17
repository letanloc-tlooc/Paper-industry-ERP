from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PurchaseOrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PurchaseOrderItemCreate(BaseModel):
    product_id: int

    quantity: Decimal = Field(
        gt=0
    )

    unit_price: Decimal = Field(
        ge=0
    )


class PurchaseOrderCreate(BaseModel):
    supplier_id: int

    expected_date: datetime | None = None

    note: str | None = Field(
        default=None,
        max_length=500
    )

    items: list[PurchaseOrderItemCreate] = Field(
        min_length=1
    )


class PurchaseOrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    received_quantity: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class PurchaseOrderResponse(BaseModel):
    id: int
    order_number: str
    supplier_id: int
    status: PurchaseOrderStatus
    order_date: datetime
    expected_date: datetime | None
    note: str | None
    created_by: int | None
    created_at: datetime

    items: list[PurchaseOrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )