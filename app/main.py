from fastapi import FastAPI,Depends
from sqlalchemy import text

from app.core.authorization import require_permission
from app.core.dependencies import get_current_user
from app.core.database import engine
from app.routers.auth import router as auth_router
from app.routers.products import router as product_router
from app.routers import warehouses
from app.routers import inventory
from app.routers import stock_movements
from app.models.user import User
from app.routers.categories import router as category_router
from app.routers.units import router as unit_router

app = FastAPI(
    title="Paper Manufacturing ERP",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(unit_router)
app.include_router(warehouses.router)
app.include_router(inventory.router)
app.include_router(stock_movements.router)
@app.get("/")
def root():
    return {
        "message": "Paper Manufacturing ERP API"
    }


@app.get("/health")
def health_check():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "OK",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "database": "disconnected",
            "detail": str(e)
        }
    
@app.get("/api/v1/auth/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }
@app.get(
    "/api/v1/test/inventory",
    dependencies=[
        Depends(
            require_permission("inventory:write")
        )
    ]
)
def test_inventory_permission():

    return {
        "message": "You have inventory:write permission"
    }