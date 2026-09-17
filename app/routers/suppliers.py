from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate
)
from app.services.supplier_service import (
    create_supplier,
    deactivate_supplier,
    get_supplier_by_id,
    get_suppliers,
    update_supplier
)


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


@router.get(
    "",
    response_model=list[SupplierResponse]
)
def read_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):

    return get_suppliers(
        db,
        skip,
        limit
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def read_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    supplier = get_supplier_by_id(
        db,
        supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    return supplier


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED
)
def create_supplier_api(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db)
):

    try:

        return create_supplier(
            db,
            supplier_data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def update_supplier_api(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):

    supplier = get_supplier_by_id(
        db,
        supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    try:

        return update_supplier(
            db,
            supplier,
            supplier_data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{supplier_id}/deactivate",
    response_model=SupplierResponse
)
def deactivate_supplier_api(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    supplier = get_supplier_by_id(
        db,
        supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    try:

        return deactivate_supplier(
            db,
            supplier
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )