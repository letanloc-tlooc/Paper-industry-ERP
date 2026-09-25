from decimal import Decimal

from pydantic import BaseModel


class MovementSummary(BaseModel):
    IN: Decimal
    OUT: Decimal
    ADJUSTMENT: Decimal


class InventoryDashboardResponse(BaseModel):
    total_inventory_items: int
    total_quantity: Decimal
    total_reserved_quantity: Decimal
    total_available_quantity: Decimal
    low_stock_items: int
    movement_summary: MovementSummary