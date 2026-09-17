from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.database import get_db

from app.models.user import User

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
)

from app.services.purchase_order_service import (
    create_purchase_order,
    get_purchase_order_by_id,
    get_purchase_orders,
)


router = APIRouter(
    prefix="/api/v1/purchase-orders",
    tags=["Purchase Orders"]
)


@router.post(
    "",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_purchase_order_api(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("purchase:create")
    )
):

    try:
        return create_purchase_order(
            db,
            data,
            current_user
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[PurchaseOrderResponse]
)
def get_purchase_order_list(
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
        require_permission("purchase:read")
    )
):

    return get_purchase_orders(
        db,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse
)
def get_purchase_order(
    purchase_order_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_permission("purchase:read")
    )
):

    order = get_purchase_order_by_id(
        db,
        purchase_order_id
    )

    if order is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )

    return order