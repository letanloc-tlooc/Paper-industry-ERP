from decimal import Decimal

from pydantic import BaseModel


class LowStockResponse(BaseModel):
    inventory_id: int

    warehouse_id: int
    product_id: int

    product_code: str
    product_name: str

    min_stock: Decimal

    quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal