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


# ============================================================
# CREATE
# ============================================================

class PurchaseOrderItemCreate(BaseModel):
    product_id: int = Field(
        gt=0,
        description="ID sản phẩm",
    )

    quantity: Decimal = Field(
        gt=0,
        description="Số lượng cần mua",
    )


class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(
        gt=0,
        description="ID nhà cung cấp",
    )

    order_date: datetime | None = None

    expected_date: datetime | None = None

    note: str | None = Field(
        default=None,
        max_length=500,
    )

    items: list[PurchaseOrderItemCreate] = Field(
        min_length=1,
        description="Danh sách sản phẩm cần mua",
    )


# ============================================================
# UPDATE
# ============================================================

class PurchaseOrderUpdate(BaseModel):
    supplier_id: int | None = None

    expected_date: datetime | None = None

    note: str | None = Field(
        default=None,
        max_length=500,
    )


# ============================================================
# RECEIVE
# ============================================================

class PurchaseOrderReceiveItem(BaseModel):
    product_id: int

    quantity: Decimal = Field(
        gt=0,
    )


class PurchaseOrderReceive(BaseModel):
    warehouse_id: int

    items: list[PurchaseOrderReceiveItem] = Field(
        min_length=1,
    )


# ============================================================
# RESPONSE
# ============================================================

class PurchaseOrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    received_quantity: Decimal

    model_config = {
        "from_attributes": True
    }


class PurchaseOrderResponse(BaseModel):
    id: int
    order_number: str
    supplier_id: int
    status: str
    order_date: datetime
    expected_date: datetime | None
    note: str | None
    created_by: int | None
    created_at: datetime
    items: list[PurchaseOrderItemResponse]

    model_config = {
        "from_attributes": True
    }