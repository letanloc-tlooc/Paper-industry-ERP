from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class InventoryReserveRequest(BaseModel):
    warehouse_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0, max_digits=15, decimal_places=3)

class InventoryReleaseRequest(BaseModel):
    warehouse_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=3,
    )

class InventoryStockOutRequest(BaseModel):
    warehouse_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=3,
    )
    reason: str | None = Field(
        default=None,
        max_length=255,
    )
    reference_type: str | None = Field(
        default=None,
        max_length=50,
    )
    reference_id: int | None = Field(
        default=None,
        gt=0,
    )

class InventoryResponse(BaseModel):
    id: int

    warehouse_id: int
    product_id: int

    quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

