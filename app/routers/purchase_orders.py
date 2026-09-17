from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderUpdate,
)

from app.services.purchase_order_service import (
    cancel_purchase_order,
    confirm_purchase_order,
    create_purchase_order,
    delete_purchase_order,
    get_purchase_order_by_id,
    get_purchase_orders,
    update_purchase_order,
)

from app.models.user import User
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"],
)


@router.get(
    "",
    response_model=list[PurchaseOrderResponse],
)
def read_purchase_orders(
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
    return get_purchase_orders(
        db,
        skip,
        limit,
    )


@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse,
)
def read_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
):
    purchase_order = get_purchase_order_by_id(
        db,
        purchase_order_id,
    )

    if purchase_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )

    return purchase_order


@router.post(
    "",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_order_api(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_purchase_order(
            db,
            data,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse,
)
def update_purchase_order_api(
    purchase_order_id: int,
    data: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
):
    purchase_order = get_purchase_order_by_id(
        db,
        purchase_order_id,
    )

    if purchase_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )

    try:
        return update_purchase_order(
            db,
            purchase_order,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{purchase_order_id}/confirm",
    response_model=PurchaseOrderResponse,
)
def confirm_purchase_order_api(
    purchase_order_id: int,
    db: Session = Depends(get_db),
):
    purchase_order = get_purchase_order_by_id(
        db,
        purchase_order_id,
    )

    if purchase_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )

    try:
        return confirm_purchase_order(
            db,
            purchase_order,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{purchase_order_id}/cancel",
    response_model=PurchaseOrderResponse,
)
def cancel_purchase_order_api(
    purchase_order_id: int,
    db: Session = Depends(get_db),
):
    purchase_order = get_purchase_order_by_id(
        db,
        purchase_order_id,
    )

    if purchase_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )

    try:
        return cancel_purchase_order(
            db,
            purchase_order,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{purchase_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_purchase_order_api(
    purchase_order_id: int,
    db: Session = Depends(get_db),
):
    purchase_order = get_purchase_order_by_id(
        db,
        purchase_order_id,
    )

    if purchase_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )

    try:
        delete_purchase_order(
            db,
            purchase_order,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )