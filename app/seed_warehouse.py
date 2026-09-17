from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.warehouse import Warehouse


WAREHOUSES = [
    {
        "code": "WH-RM",
        "name": "Kho nguyên liệu",
        "location": "Nhà máy số 1",
    },
    {
        "code": "WH-PKG",
        "name": "Kho bao bì",
        "location": "Nhà máy số 1",
    },
    {
        "code": "WH-FG",
        "name": "Kho thành phẩm",
        "location": "Nhà máy số 1",
    },
]


def seed_warehouses():
    db = SessionLocal()

    try:
        for data in WAREHOUSES:
            existing = db.scalar(
                select(Warehouse).where(
                    Warehouse.code == data["code"]
                )
            )

            if existing:
                print(f"SKIP: {data['code']} already exists")
                continue

            warehouse = Warehouse(
                code=data["code"],
                name=data["name"],
                location=data["location"],
                is_active=True,
            )

            db.add(warehouse)
            print(f"CREATE: {data['code']}")

        db.commit()
        print("Warehouse seed completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_warehouses()