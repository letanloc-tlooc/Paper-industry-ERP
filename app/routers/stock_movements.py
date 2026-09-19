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
from app.schemas.stock_movement import (
    StockMovementCreate,
    StockMovementResponse
)
from app.services.stock_movement_service import (
    create_stock_movement,
    get_stock_movement_by_id,
    get_stock_movements,
    get_stock_movements_by_product,
    get_stock_movements_by_warehouse,
)


router = APIRouter(
    prefix="/api/v1/stock-movements",
    tags=["Stock Movements"]
)


@router.post(
    "",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def create_stock_movement_api(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:write")
    )
):

    try:

        return create_stock_movement(
            db,
            movement_data,
            current_user
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[StockMovementResponse]
)
def get_stock_movement_list(
    warehouse_id: int | None = Query(
        default=None,
        ge=1
    ),
    product_id: int | None = Query(
        default=None,
        ge=1
    ),
    movement_type: str | None = None,
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

    return get_stock_movements(
        db,
        warehouse_id=warehouse_id,
        product_id=product_id,
        movement_type=movement_type,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{movement_id}",
    response_model=StockMovementResponse
)
def get_stock_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory:read")
    )
):

    movement = get_stock_movement_by_id(
        db,
        movement_id
    )

    if movement is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock movement not found"
        )

    return movement

@router.get(
    "/warehouse/{warehouse_id}",
    response_model=list[StockMovementResponse],
)
def read_stock_movements_by_warehouse(
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
        return get_stock_movements_by_warehouse(
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
    response_model=list[StockMovementResponse],
)
def read_stock_movements_by_product(
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
        return get_stock_movements_by_product(
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