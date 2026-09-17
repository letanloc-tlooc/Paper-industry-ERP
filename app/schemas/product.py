from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class ProductType(str, Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    PACKAGING = "PACKAGING"
    SEMI_FINISHED = "SEMI_FINISHED"
    FINISHED_GOOD = "FINISHED_GOOD"

class ProductCreate(BaseModel):
    code: str = Field(
        min_length=1,
        max_length=50
    )

    name: str = Field(
        min_length=1,
        max_length=150
    )

    category_id: int

    unit_id: int

    product_type: ProductType 
    # = Field(
    #     min_length=1,
    #     max_length=30
    # )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    min_stock: float = Field(
        default=0,
        ge=0
    )


class ProductUpdate(BaseModel):
    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    category_id: int | None = None

    unit_id: int | None = None

    product_type: ProductType | None = None
    # | None = Field(
    #     default=None,
    #     min_length=1,
    #     max_length=30
    # )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    min_stock: float | None = Field(
        default=None,
        ge=0
    )

    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    code: str
    name: str

    category_id: int
    unit_id: int

    product_type: ProductType 

    description: str | None

    min_stock: float

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )