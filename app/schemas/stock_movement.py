from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class StockMovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"


class StockMovementCreate(BaseModel):
    warehouse_id: int
    product_id: int

    movement_type: StockMovementType

    quantity_change: Decimal

    reason: str | None = Field(
        default=None,
        max_length=255
    )

    reference_type: str | None = Field(
        default=None,
        max_length=50
    )

    reference_id: int | None = Field(
        default=None,
        gt=0
    )


class StockMovementResponse(BaseModel):
    id: int

    warehouse_id: int
    product_id: int

    movement_type: StockMovementType

    quantity_change: Decimal

    reason: str | None

    reference_type: str | None
    reference_id: int | None

    created_by: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )