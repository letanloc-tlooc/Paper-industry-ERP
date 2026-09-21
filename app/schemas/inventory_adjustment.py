from decimal import Decimal

from pydantic import BaseModel, Field


class InventoryAdjustmentCreate(BaseModel):
    warehouse_id: int = Field(gt=0)
    product_id: int = Field(gt=0)

    quantity_change: Decimal

    reason: str = Field(
        min_length=1,
        max_length=255,
    )