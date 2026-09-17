from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate
)
from app.services.warehouse_service import (
    create_warehouse,
    deactivate_warehouse,
    get_warehouse_by_id,
    get_warehouses,
    update_warehouse
)


router = APIRouter(
    prefix="/api/v1/warehouses",
    tags=["Warehouses"]
)


@router.post(
    "",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_warehouse_api(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:write")
    )
):
    try:
        return create_warehouse(
            db,
            warehouse_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[WarehouseResponse]
)
def get_warehouse_list(
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
    return get_warehouses(
        db,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:read")
    )
):
    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    return warehouse


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def update_warehouse_api(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:write")
    )
):
    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    try:
        return update_warehouse(
            db,
            warehouse,
            warehouse_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{warehouse_id}/deactivate",
    response_model=WarehouseResponse
)
def deactivate_warehouse_api(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:write")
    )
):
    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    try:
        return deactivate_warehouse(
            db,
            warehouse
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )