from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.unit import (
    UnitCreate,
    UnitResponse,
    UnitUpdate,
)
from app.services.unit_service import (
    create_unit,
    get_unit_by_id,
    get_units,
    update_unit,
)


router = APIRouter(
    prefix="/api/v1/units",
    tags=["Units"]
)


@router.post(
    "",
    response_model=UnitResponse,
    status_code=status.HTTP_201_CREATED
)
def create_unit_api(
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("product:create")
    )
):
    try:
        return create_unit(db, unit_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[UnitResponse]
)
def get_unit_list(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("product:read")
    )
):
    return get_units(
        db,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{unit_id}",
    response_model=UnitResponse
)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("product:read")
    )
):
    unit = get_unit_by_id(
        db,
        unit_id
    )

    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )

    return unit


@router.put(
    "/{unit_id}",
    response_model=UnitResponse
)
def update_unit_api(
    unit_id: int,
    unit_data: UnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("product:update")
    )
):
    unit = get_unit_by_id(
        db,
        unit_id
    )

    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )

    try:
        return update_unit(
            db,
            unit,
            unit_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )