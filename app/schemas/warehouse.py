from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WarehouseCreate(BaseModel):
    code: str = Field(
        min_length=1,
        max_length=50
    )

    name: str = Field(
        min_length=1,
        max_length=100
    )

    location: str | None = Field(
        default=None,
        max_length=255
    )


class WarehouseUpdate(BaseModel):
    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    location: str | None = Field(
        default=None,
        max_length=255
    )

    is_active: bool | None = None


class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str
    location: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )