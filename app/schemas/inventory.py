from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


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

