from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.inventory import InventoryResponse
from app.services.inventory_service import (
    get_inventories,
    get_inventory_by_product,
    get_inventory_by_warehouse,
    get_inventory_by_warehouse_and_product,
    get_inventory_by_id
)


router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory"]
)


@router.get(
    "",
    response_model=list[InventoryResponse]
)
def get_inventory_list(
    warehouse_id: int | None = Query(
        default=None,
        ge=1
    ),
    product_id: int | None = Query(
        default=None,
        ge=1
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:read")
    )
):
    return get_inventories(
        db,
        warehouse_id=warehouse_id,
        product_id=product_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def get_inventory_detail(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:read")
    )
):
    inventory = get_inventory_by_id(
        db,
        inventory_id
    )

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    return inventory

@router.get(
    "/warehouse/{warehouse_id}",
    response_model=list[InventoryResponse],
)
def read_inventory_by_warehouse(
    warehouse_id: int,
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_inventory_by_warehouse(
            db,
            warehouse_id,
            skip,
            limit,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/product/{product_id}",
    response_model=list[InventoryResponse],
)
def read_inventory_by_product(
    product_id: int,
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_inventory_by_product(
            db,
            product_id,
            skip,
            limit,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/warehouse/{warehouse_id}/product/{product_id}",
    response_model=InventoryResponse,
)
def read_inventory_by_warehouse_and_product(
    warehouse_id: int,
    product_id: int,
    db: Session = Depends(get_db),
):
    try:
        inventory = get_inventory_by_warehouse_and_product(
            db,
            warehouse_id,
            product_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found",
        )

    return inventory