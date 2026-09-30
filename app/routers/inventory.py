from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user

from app.core.authorization import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryReleaseRequest,
    InventoryReserveRequest,
    InventoryStockOutRequest,
    InventoryResponse
)
from app.schemas.low_stock import LowStockResponse
from app.schemas.inventory_dashboard import InventoryDashboardResponse
from app.schemas.inventory_adjustment import (
    InventoryAdjustmentCreate,
)
from app.services.inventory_adjustment_service import (
    adjust_inventory,
)
from app.services.low_stock_service import (
    get_low_stock_items,
)
from app.services.inventory_dashboard_service import get_inventory_dashboard
from app.services.inventory_service import (
    get_inventories,
    get_inventory_by_product,
    get_inventory_by_warehouse,
    get_inventory_by_warehouse_and_product,
    get_inventory_by_id,
    reserve_stock,
    release_stock,
    stock_out
)


router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory"],
    dependencies=[Depends(get_current_user)],
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
    "/dashboard",
    response_model=InventoryDashboardResponse,
)
def read_inventory_dashboard(
    warehouse_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter dashboard by warehouse ID",
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_inventory_dashboard(
            db=db,
            warehouse_id=warehouse_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


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

@router.post(
    "/adjust",
    response_model=InventoryResponse,
)
def adjust_inventory_quantity(
    data: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return adjust_inventory(
            db=db,
            data=data,
            current_user_id=current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get(
    "/low-stock",
    response_model=list[LowStockResponse],
)
def read_low_stock_items(
    warehouse_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter by warehouse ID",
    ),
    product_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter by product ID",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_low_stock_items(
            db=db,
            warehouse_id=warehouse_id,
            product_id=product_id,
            skip=skip,
            limit=limit,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@router.post(
    "/reserve",
    response_model=InventoryResponse,
)
def reserve_inventory_stock(
    data: InventoryReserveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user
    ),
):
    try:
        return reserve_stock(
            db=db,
            warehouse_id=data.warehouse_id,
            product_id=data.product_id,
            quantity=data.quantity,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/release",
    response_model=InventoryResponse,
)
def release_inventory_stock(
    data: InventoryReleaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return release_stock(
            db=db,
            warehouse_id=data.warehouse_id,
            product_id=data.product_id,
            quantity=data.quantity,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/stock-out",
    response_model=InventoryResponse,
)
def stock_out_inventory(
    data: InventoryStockOutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return stock_out(
            db=db,
            warehouse_id=data.warehouse_id,
            product_id=data.product_id,
            quantity=data.quantity,
            reason=data.reason,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            current_user_id=current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
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