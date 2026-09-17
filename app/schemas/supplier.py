from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SupplierBase(BaseModel):
    code: str
    name: str
    tax_code: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    tax_code: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )